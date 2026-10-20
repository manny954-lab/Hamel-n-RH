"""Endpoints de incidencias y justificantes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.models.incidents import Incidencia, Justificante
from app.models.employees import Empleado
from app.repositories import incidencia_repo, justificante_repo
from app.services.justificantes import (
    crear_justificante,
    decidir_justificante,
    listar_justificantes_pendientes,
    ESTADOS_VALIDOS,
)
from app.schemas import JustificanteCreate, JustificanteOut

router = APIRouter(prefix="/api/v1/incidencias", tags=["Incidencias y justificantes"])


@router.get("", response_model=list[dict])
def listar_incidencias(
    empleado_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("incidencias.leer")),
):
    q = (
        db.query(Incidencia, Empleado)
        .outerjoin(Empleado, Incidencia.empleado_id == Empleado.id)
        .order_by(Incidencia.fecha.desc())
    )
    if empleado_id:
        q = q.filter(Incidencia.empleado_id == empleado_id)
    if estado:
        q = q.filter(Incidencia.estado == estado)
    filas = q.offset(skip).limit(limit).all()
    return [
        {
            "id": str(i.id),
            "empleado_id": str(i.empleado_id),
            "numero_empleado": emp.numero_empleado if emp else "",
            "nombre_empleado": (
                f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip()
                if emp
                else ""
            ),
            "evento_asistencia_id": str(i.evento_asistencia_id)
            if i.evento_asistencia_id
            else None,
            "fecha": str(i.fecha),
            "tipo_incidencia": i.tipo_incidencia,
            "minutos_retardo": i.minutos_retardo,
            "tiempo_incidencia_minutos": i.tiempo_incidencia_minutos,
            "regla_aplicada": i.regla_aplicada,
            "justificada": i.justificada,
            "estado": i.estado,
        }
        for i, emp in filas
    ]


# ============================================================================
# RUTAS ESPECÍFICAS DE JUSTIFICANTES (ANTES que /{incidencia_id}
# para que FastAPI no confunda "justificantes" con un UUID)
# ============================================================================

@router.get("/justificantes", response_model=list[dict])
def listar_justificantes(
    empleado_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("justificantes.leer")),
):
    q = (
        db.query(Justificante, Empleado)
        .outerjoin(Empleado, Justificante.empleado_id == Empleado.id)
        .order_by(Justificante.fecha_solicitud.desc())
    )
    if empleado_id:
        q = q.filter(Justificante.empleado_id == empleado_id)
    if estado:
        q = q.filter(Justificante.estado == estado)
    filas = q.all()
    return [
        {
            "id": str(j.id),
            "empleado_id": str(j.empleado_id),
            "numero_empleado": emp.numero_empleado if emp else "",
            "nombre_empleado": (
                f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip()
                if emp
                else ""
            ),
            "tipo": j.tipo,
            "fecha_incidencia": str(j.fecha_incidencia),
            "descripcion": j.descripcion,
            "estado": j.estado,
            "fecha_solicitud": j.fecha_solicitud.isoformat(),
        }
        for j, emp in filas
    ]


@router.get("/justificantes/pendientes", response_model=list)
def justificantes_pendientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("justificantes.leer")),
):
    return listar_justificantes_pendientes(db)


@router.post("/justificantes", response_model=JustificanteOut, status_code=status.HTTP_201_CREATED)
def registrar_justificante(
    datos: JustificanteCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("justificantes.leer")),
):
    try:
        return crear_justificante(
            db,
            empleado_id=datos.empleado_id,
            tipo=datos.tipo,
            fecha_incidencia=datos.fecha_incidencia,
            descripcion=datos.descripcion,
            usuario=usuario,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/justificantes/{justificante_id}/decidir")
def decidir_justificante_endpoint(
    justificante_id: UUID,
    estado: str,
    motivo: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("justificantes.aprobar")),
):
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado no válido. Use uno de: {', '.join(ESTADOS_VALIDOS)}")
    try:
        return decidir_justificante(
            db, justificante_id=justificante_id, estado=estado,
            motivo=motivo, usuario=usuario,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# RUTA CON PARÁMETRO DE RUTA (DESPUÉS de todas las específicas)
# ============================================================================

@router.get("/{incidencia_id}", response_model=dict)
def obtener_incidencia(
    incidencia_id: UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("incidencias.leer")),
):
    inc = incidencia_repo.get(db, incidencia_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada.")
    emp = db.query(Empleado).filter(Empleado.id == inc.empleado_id).first()
    return {
        "id": str(inc.id),
        "empleado_id": str(inc.empleado_id),
        "numero_empleado": emp.numero_empleado if emp else "",
        "nombre_empleado": (
            f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip()
            if emp
            else ""
        ),
        "fecha": str(inc.fecha),
        "tipo_incidencia": inc.tipo_incidencia,
        "minutos_retardo": inc.minutos_retardo,
        "tiempo_incidencia_minutos": inc.tiempo_incidencia_minutos,
        "regla_aplicada": inc.regla_aplicada,
        "justificada": inc.justificada,
        "estado": inc.estado,
    }
