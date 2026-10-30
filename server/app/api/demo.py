"""Endpoints de demostración: generación masiva de asistencias, faltas y limpieza.

Estos endpoints son para poblar rápidamente el sistema con datos realistas
durante una demostración de venta. No se recomiendan en producción.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.services import demo
from app.services.auth import escribir_auditoria

router = APIRouter(prefix="/api/v1/demo", tags=["Demostración"])


@router.post("/generar-asistencias", response_model=dict)
def generar_asistencias(
    dias_atras: int = 5,
    request: Request = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("asistencia.registrar")),
):
    """Genera asistencias realistas para todos los empleados activos en los
    últimos N días (simulador, ideal para demostraciones)."""
    if dias_atras < 1 or dias_atras > 30:
        raise HTTPException(
            status_code=400, detail="dias_atras debe estar entre 1 y 30."
        )
    try:
        resultado = demo.generar_asistencias_demo(
            db, dias_atras=dias_atras, usuario=usuario
        )
        escribir_auditoria(
            db, usuario=usuario, operacion="generar_asistencias_demo",
            entidad="demo", registro_id="demo",
            valor_nuevo=str(resultado),
            motivo="Generación masiva de asistencias para demostración",
            direccion_ip=request.client.host if request and request.client else None,
        )
        return {
            "mensaje": "Asistencias de demostración generadas correctamente.",
            **resultado,
        }
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generar-faltas", response_model=dict)
def generar_faltas(
    fecha: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("asistencia.registrar")),
):
    """Genera incidencias de tipo 'falta' para empleados sin entrada en la
    fecha indicada (por defecto ayer)."""
    fecha_obj = None
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
        except ValueError:
            raise HTTPException(status_code=400, detail="Fecha inválida (usa YYYY-MM-DD).")
    try:
        resultado = demo.generar_faltas_automaticas(
            db, fecha=fecha_obj, usuario=usuario
        )
        escribir_auditoria(
            db, usuario=usuario, operacion="generar_faltas_demo",
            entidad="demo", registro_id="demo",
            valor_nuevo=str(resultado),
            motivo="Generación automática de faltas para demostración",
            direccion_ip=request.client.host if request and request.client else None,
        )
        return {
            "mensaje": "Faltas generadas correctamente.",
            **resultado,
        }
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/limpiar", response_model=dict)
def limpiar_demo(
    request: Request = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("configuracion.escribir")),
):
    """Elimina eventos de asistencia e incidencias (mantiene catálogos y empleados)."""
    try:
        resultado = demo.limpiar_datos_demo(db)
        escribir_auditoria(
            db, usuario=usuario, operacion="limpiar_demo",
            entidad="demo", registro_id="demo",
            valor_nuevo=str(resultado),
            motivo="Limpieza de datos de demostración",
            direccion_ip=request.client.host if request and request.client else None,
        )
        return {
            "mensaje": "Datos de demostración limpiados.",
            **resultado,
        }
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
