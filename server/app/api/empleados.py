"""Endpoints de empleados."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.models.employees import Empleado
from app.models.catalogs import AsignacionHorario, Departamento, Horario
from app.models.catalogs import AsignacionHorario as AH
from app.repositories import empleado_repo, asignacion_horario_repo, horario_repo
from app.services.empleados import (
    crear_empleado,
    actualizar_empleado,
    cambiar_estado_empleado,
    validar_empleado_data,
)
from app.services.auth import escribir_auditoria
from app.schemas import EmpleadoCreate, EmpleadoOut
from pydantic import BaseModel
from datetime import date, datetime, timezone


class AsignarHorario(BaseModel):
    horario_id: UUID
    fecha_inicio_vigencia: str  # YYYY-MM-DD
    fecha_fin_vigencia: Optional[str] = None

router = APIRouter(prefix="/api/v1/empleados", tags=["Empleados"])


@router.get("", response_model=list[dict])
def listar_empleados(
    departamento_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("empleados.leer")),
):
    q = (
        db.query(Empleado, Departamento.nombre.label("departamento_nombre"))
        .outerjoin(Departamento, Empleado.departamento_id == Departamento.id)
        .filter(Empleado.eliminado_en.is_(None))
    )
    if departamento_id:
        q = q.filter(Empleado.departamento_id == departamento_id)
    if estado:
        q = q.filter(Empleado.estado == estado)
    filas = q.all()
    return [
        {
            "id": str(e.id),
            "numero_empleado": e.numero_empleado,
            "nombre": e.nombre,
            "apellido_paterno": e.apellido_paterno,
            "apellido_materno": e.apellido_materno,
            "departamento_id": str(e.departamento_id),
            "departamento_nombre": departamento_nombre or "",
            "puesto_id": str(e.puesto_id) if e.puesto_id else None,
            "fecha_ingreso": str(e.fecha_ingreso),
            "estado": e.estado,
            "fecha_creacion": e.fecha_creacion.isoformat(),
        }
        for e, departamento_nombre in filas
    ]


@router.post("", response_model=EmpleadoOut, status_code=status.HTTP_201_CREATED)
def crear_empleado_endpoint(
    datos: EmpleadoCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("empleados.escribir")),
):
    try:
        return crear_empleado(db, datos=datos.model_dump(), usuario=usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{empleado_id}", response_model=EmpleadoOut)
def obtener_empleado(
    empleado_id: UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("empleados.leer")),
):
    e = empleado_repo.get(db, empleado_id)
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")
    return e


@router.patch("/{empleado_id}", response_model=EmpleadoOut)
def actualizar_empleado_endpoint(
    empleado_id: UUID,
    datos: EmpleadoCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("empleados.escribir")),
):
    try:
        return actualizar_empleado(
            db, empleado_id=empleado_id, datos=datos.model_dump(), usuario=usuario
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{empleado_id}/estado")
def cambiar_estado_endpoint(
    empleado_id: UUID,
    estado: str,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("empleados.escribir")),
):
    try:
        return cambiar_estado_empleado(db, empleado_id=empleado_id, estado=estado, usuario=usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{empleado_id}/horario")
def asignar_horario_empleado(
    empleado_id: UUID,
    datos: AsignarHorario,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("empleados.escribir")),
):
    empleado = empleado_repo.get(db, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")
    horario = horario_repo.get(db, datos.horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado.")
    fi = date.fromisoformat(datos.fecha_inicio_vigencia)
    ff = date.fromisoformat(datos.fecha_fin_vigencia) if datos.fecha_fin_vigencia else None
    asignacion = AsignacionHorario(
        empleado_id=empleado_id,
        horario_id=datos.horario_id,
        fecha_inicio_vigencia=fi,
        fecha_fin_vigencia=ff,
    )
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)

    escribir_auditoria(
        db, usuario=usuario, operacion="asignar_horario", entidad="empleado",
        registro_id=str(empleado_id),
        valor_nuevo=f"horario {horario.codigo} desde {fi}",
        motivo="Asignación de horario a empleado",
        direccion_ip=request.client.host if request and request.client else None,
    )
    return {"asignacion_id": str(asignacion.id), "horario_id": str(horario.id)}


@router.delete("/{empleado_id}", response_model=dict)
def eliminar_empleado(
    empleado_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("empleados.eliminar")),
):
    """Eliminar empleado (solo Administrador)."""
    empleado = empleado_repo.get(db, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")

    nombre_empleado = f"{empleado.nombre} {empleado.apellido_paterno} {empleado.apellido_materno or ''}".strip()

    # Eliminación lógica: marcar como eliminado en lugar de borrar físicamente
    empleado.eliminado_en = datetime.now(timezone.utc)
    empleado.estado = "eliminado"
    db.add(empleado)
    db.commit()

    escribir_auditoria(
        db, usuario=usuario, operacion="eliminar", entidad="empleado",
        registro_id=str(empleado_id),
        valor_anterior=f"{empleado.numero_empleado} - {nombre_empleado}",
        motivo="Eliminación de empleado (eliminación lógica)",
        direccion_ip=request.client.host if request and request.client else None,
    )
    return {"mensaje": f"Empleado {empleado.numero_empleado} - {nombre_empleado} eliminado correctamente."}
