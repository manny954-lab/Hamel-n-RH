"""Endpoints de prenómina y reportes básicos."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.models.payroll import PeriodoNomina
from app.repositories import periodo_nomina_repo
from app.services.payroll import (
    crear_periodo,
    calcular_prenomina,
    proponer_ajuste,
    decidir_propuesta_ajuste,
    cerrar_periodo,
)
from app.schemas import PeriodoNominaCreate, PeriodoNominaOut, PropuestaAjusteCreate, PropuestaAjusteOut

router = APIRouter(prefix="/api/v1/nomina", tags=["Nómina y prenómina"])


@router.post("/periodos", response_model=PeriodoNominaOut, status_code=status.HTTP_201_CREATED)
def crear_periodo_endpoint(
    datos: PeriodoNominaCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("nomina.calcular")),
):
    try:
        return crear_periodo(db, datos=datos.model_dump(), usuario=usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/periodos", response_model=list[dict])
def listar_periodos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("nomina.leer")),
):
    filas = db.query(PeriodoNomina).order_by(PeriodoNomina.fecha_inicio.desc()).all()
    return [
        {
            "id": str(p.id),
            "nombre": p.nombre,
            "fecha_inicio": str(p.fecha_inicio),
            "fecha_fin": str(p.fecha_fin),
            "estado": p.estado,
            "fecha_creacion": p.fecha_creacion.isoformat(),
        }
        for p in filas
    ]


@router.post("/periodos/{periodo_id}/calcular", response_model=list[dict])
def calcular_prenomina_endpoint(
    periodo_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("nomina.calcular")),
):
    try:
        resultados = calcular_prenomina(db, periodo_id=periodo_id, usuario=usuario)
        return [
            {
                "id": str(r.id),
                "periodo_nomina_id": str(r.periodo_nomina_id),
                "empleado_id": str(r.empleado_id),
                "sueldo_base_periodo": r.sueldo_base_periodo,
                "dias_laborables": r.dias_laborables,
                "dias_asistidos": r.dias_asistidos,
                "faltas_registradas": r.faltas_registradas,
                "faltas_justificadas": r.faltas_justificadas,
                "retardos": r.retardos,
                "minutos_retardo_acumulados": r.minutos_retardo_acumulados,
                "ajustes_propuestos": float(r.ajustes_propuestos),
                "ajustes_aprobados": float(r.ajustes_aprobados),
                "total_percepciones": float(r.total_percepciones),
                "total_preliminar": float(r.total_preliminar),
                "estado_aprobacion": r.estado_aprobacion,
                "fecha_calculo": r.fecha_calculo.isoformat(),
            }
            for r in resultados
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/periodos/{periodo_id}/resultados", response_model=list[dict])
def resultados_prenomina(
    periodo_id: UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("nomina.leer")),
):
    from app.models.payroll import ResultadoNomina
    filas = (
        db.query(ResultadoNomina)
        .filter(ResultadoNomina.periodo_nomina_id == periodo_id)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "empleado_id": str(r.empleado_id),
            "sueldo_base_periodo": float(r.sueldo_base_periodo),
            "dias_laborables": r.dias_laborables,
            "dias_asistidos": r.dias_asistidos,
            "faltas_registradas": r.faltas_registradas,
            "faltas_justificadas": r.faltas_justificadas,
            "retardos": r.retardos,
            "minutos_retardo_acumulados": r.minutos_retardo_acumulados,
            "ajustes_propuestos": float(r.ajustes_propuestos),
            "ajustes_aprobados": float(r.ajustes_aprobados),
            "total_percepciones": float(r.total_percepciones),
            "total_preliminar": float(r.total_preliminar),
            "estado_aprobacion": r.estado_aprobacion,
        }
        for r in filas
    ]


@router.post("/ajustes", response_model=PropuestaAjusteOut, status_code=status.HTTP_201_CREATED)
def proponer_ajuste_endpoint(
    datos: PropuestaAjusteCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("nomina.calcular")),
):
    return proponer_ajuste(db, datos=datos.model_dump(), usuario=usuario)


@router.post("/ajustes/{propuesta_id}/decidir")
def decidir_ajuste_endpoint(
    propuesta_id: UUID,
    estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("nomina.cerrar")),
):
    if estado not in ("aprobado", "rechazado"):
        raise HTTPException(status_code=400, detail="Estado debe ser 'aprobado' o 'rechazado'")
    try:
        return decidir_propuesta_ajuste(db, propuesta_id=propuesta_id, estado=estado, usuario=usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/periodos/{periodo_id}/cerrar")
def cerrar_periodo_endpoint(
    periodo_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_permiso("nomina.cerrar")),
):
    try:
        return cerrar_periodo(db, periodo_id=periodo_id, usuario=usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
