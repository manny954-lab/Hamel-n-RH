"""Endpoints de registro de asistencia."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.models.attendance import EventoAsistencia
from app.models.employees import Empleado
from app.repositories import evento_asistencia_repo
from app.services.asistencia import (
    registrar_evento,
    corregir_evento,
    listar_eventos_pendientes_salida,
)
from app.schemas import EventoAsistenciaCreate, EventoAsistenciaOut

router = APIRouter(prefix="/api/v1/asistencia", tags=["Asistencia"])


@router.post("/eventos", response_model=EventoAsistenciaOut, status_code=status.HTTP_201_CREATED)
def registrar_evento_endpoint(
    datos: EventoAsistenciaCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("asistencia.registrar")),
):
    try:
        return registrar_evento(
            db,
            empleado_id=datos.empleado_id,
            tipo_evento=datos.tipo_evento,
            fecha_hora=datos.fecha_hora,
            metodo_registro=datos.metodo_registro,
            usuario=usuario,
            dispositivo_id=datos.dispositivo_id,
            observaciones=datos.observaciones,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/eventos", response_model=list[dict])
def listar_eventos(
    empleado_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("asistencia.registrar")),
):
    q = (
        db.query(EventoAsistencia, Empleado)
        .outerjoin(Empleado, EventoAsistencia.empleado_id == Empleado.id)
        .order_by(EventoAsistencia.fecha_hora.desc())
    )
    if empleado_id:
        q = q.filter(EventoAsistencia.empleado_id == empleado_id)
    filas = q.offset(skip).limit(limit).all()
    return [
        {
            "id": str(e.id),
            "empleado_id": str(e.empleado_id),
            "numero_empleado": emp.numero_empleado if emp else "",
            "nombre_empleado": f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip()
            if emp
            else "",
            "tipo_evento": e.tipo_evento,
            "fecha_hora": e.fecha_hora.isoformat(),
            "metodo_registro": e.metodo_registro,
            "resultado_validacion": e.resultado_validacion,
            "incidencia_detectada": e.incidencia_detectada,
        }
        for e, emp in filas
    ]


@router.patch("/eventos/{evento_id}/corregir", response_model=dict)
def corregir_evento_endpoint(
    evento_id: UUID,
    datos: dict,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("asistencia.ajustar")),
):
    try:
        ajuste = corregir_evento(
            db,
            evento_id=evento_id,
            valor_corregido=datos,
            motivo=datos.get("motivo", "Corrección de evento"),
            usuario=usuario,
            aprobado_por=None,
        )
        return {"ajuste_id": str(ajuste.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pendientes-salida", response_model=list[dict])
def eventos_sin_salida(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("asistencia.registrar")),
):
    filas = listar_eventos_pendientes_salida(db)
    return [
        {
            "id": str(e.id),
            "empleado_id": str(e.empleado_id),
            "numero_empleado": e.empleado.numero_empleado if e.empleado else "",
            "nombre_empleado": (
                f"{e.empleado.nombre} {e.empleado.apellido_paterno} {e.empleado.apellido_materno or ''}".strip()
                if e.empleado
                else ""
            ),
            "fecha_hora": e.fecha_hora.isoformat(),
            "tipo_evento": e.tipo_evento,
        }
        for e in filas
    ]
