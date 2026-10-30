"""Endpoints de reportes con exportación CSV y múltiples vistas para demostración."""

import csv
import io
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.models.employees import Empleado
from app.models.incidents import Incidencia, Justificante
from app.models.attendance import EventoAsistencia
from app.models.payroll import PeriodoNomina, ResultadoNomina

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


# ---------------------------------------------------------------------------
# Reporte quincenal (tabla de incidencias con exportación CSV)
# ---------------------------------------------------------------------------
@router.get("/quincenal")
def reporte_quincenal(
    fecha_inicio: str,
    fecha_fin: str,
    formato: Optional[str] = "json",
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Reporte quincenal de incidencias con exportación CSV."""
    try:
        date.fromisoformat(fecha_inicio)
        date.fromisoformat(fecha_fin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Fechas inválidas (usa YYYY-MM-DD).")

    q = (
        db.query(Incidencia, Empleado)
        .join(Empleado, Incidencia.empleado_id == Empleado.id)
        .filter(Incidencia.fecha >= fecha_inicio)
        .filter(Incidencia.fecha <= fecha_fin)
        .order_by(Incidencia.fecha, Empleado.numero_empleado)
        .all()
    )
    filas = []
    for inc, emp in q:
        filas.append({
            "numero_empleado": emp.numero_empleado,
            "nombre": f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip(),
            "departamento": emp.departamento.nombre if emp.departamento else "",
            "fecha_incidencia": str(inc.fecha),
            "tipo_incidencia": inc.tipo_incidencia,
            "minutos_retardo": inc.minutos_retardo,
            "tiempo_incidencia_minutos": inc.tiempo_incidencia_minutos,
            "justificada": "Sí" if inc.justificada else "No",
            "estado": inc.estado,
            "regla_aplicada": inc.regla_aplicada,
        })

    if formato == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "numero_empleado", "nombre", "departamento", "fecha_incidencia",
                "tipo_incidencia", "minutos_retardo", "tiempo_incidencia_minutos",
                "justificada", "estado", "regla_aplicada",
            ],
        )
        writer.writeheader()
        writer.writerows(filas)
        contenido = output.getvalue().encode("utf-8")
        return StreamingResponse(
            iter([contenido]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_quincenal_{fecha_inicio}_a_{fecha_fin}.csv"
            },
        )

    return {
        "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
        "total": len(filas),
        "filas": filas,
    }


# ---------------------------------------------------------------------------
# Reporte de asistencia (entradas y salidas por empleado)
# ---------------------------------------------------------------------------
@router.get("/asistencia")
def reporte_asistencia(
    fecha_inicio: str,
    fecha_fin: str,
    formato: Optional[str] = "json",
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Reporte de eventos de asistencia (entradas/salidas) en un rango."""
    try:
        date.fromisoformat(fecha_inicio)
        date.fromisoformat(fecha_fin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Fechas inválidas (usa YYYY-MM-DD).")

    q = (
        db.query(EventoAsistencia, Empleado)
        .join(Empleado, EventoAsistencia.empleado_id == Empleado.id)
        .filter(EventoAsistencia.fecha_hora >= fecha_inicio)
        .filter(EventoAsistencia.fecha_hora <= fecha_fin + " 23:59:59")
        .order_by(EventoAsistencia.fecha_hora.desc())
        .all()
    )
    filas = []
    for ev, emp in q:
        filas.append({
            "numero_empleado": emp.numero_empleado,
            "nombre": f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip(),
            "departamento": emp.departamento.nombre if emp.departamento else "",
            "tipo_evento": ev.tipo_evento,
            "fecha_hora": ev.fecha_hora.isoformat(),
            "metodo_registro": ev.metodo_registro,
            "resultado": ev.resultado_validacion,
            "incidencia": "Sí" if ev.incidencia_detectada else "No",
        })

    if formato == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "numero_empleado", "nombre", "departamento", "tipo_evento",
                "fecha_hora", "metodo_registro", "resultado", "incidencia",
            ],
        )
        writer.writeheader()
        writer.writerows(filas)
        contenido = output.getvalue().encode("utf-8")
        return StreamingResponse(
            iter([contenido]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_asistencia_{fecha_inicio}_a_{fecha_fin}.csv"
            },
        )

    return {
        "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
        "total": len(filas),
        "filas": filas,
    }


# ---------------------------------------------------------------------------
# Reporte de nómina (prenómina por empleado en un periodo)
# ---------------------------------------------------------------------------
@router.get("/nomina")
def reporte_nomina(
    periodo_id: str,
    formato: Optional[str] = "json",
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Reporte de resultados de prenómina de un periodo."""
    from uuid import UUID as _UUID

    try:
        pid = _UUID(periodo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de periodo inválido.")

    periodo = db.query(PeriodoNomina).filter(PeriodoNomina.id == pid).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo de nómina no encontrado.")

    q = (
        db.query(ResultadoNomina, Empleado)
        .join(Empleado, ResultadoNomina.empleado_id == Empleado.id)
        .filter(ResultadoNomina.periodo_nomina_id == pid)
        .order_by(Empleado.numero_empleado)
        .all()
    )
    filas = []
    for res, emp in q:
        filas.append({
            "numero_empleado": emp.numero_empleado,
            "nombre": f"{emp.nombre} {emp.apellido_paterno} {emp.apellido_materno or ''}".strip(),
            "departamento": emp.departamento.nombre if emp.departamento else "",
            "sueldo_base": res.sueldo_base_periodo,
            "dias_laborables": res.dias_laborables,
            "dias_asistidos": res.dias_asistidos,
            "faltas_registradas": res.faltas_registradas,
            "faltas_justificadas": res.faltas_justificadas,
            "retardos": res.retardos,
            "minutos_retardo": res.minutos_retardo_acumulados,
            "ajustes_propuestos": res.ajustes_propuestos,
            "ajustes_aprobados": res.ajustes_aprobados,
            "total_preliminar": res.total_preliminar,
            "estado": res.estado_aprobacion,
        })
    total_nomina = sum(f["total_preliminar"] for f in filas)

    if formato == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "numero_empleado", "nombre", "departamento", "sueldo_base",
                "dias_laborables", "dias_asistidos", "faltas_registradas",
                "faltas_justificadas", "retardos", "minutos_retardo",
                "ajustes_propuestos", "ajustes_aprobados", "total_preliminar", "estado",
            ],
        )
        writer.writeheader()
        writer.writerows(filas)
        contenido = output.getvalue().encode("utf-8")
        return StreamingResponse(
            iter([contenido]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=prenomina_{periodo.nombre}.csv"
            },
        )

    return {
        "periodo": {
            "id": str(periodo.id),
            "nombre": periodo.nombre,
            "inicio": str(periodo.fecha_inicio),
            "fin": str(periodo.fecha_fin),
            "estado": periodo.estado,
        },
        "total_nomina": round(total_nomina, 2),
        "total_empleados": len(filas),
        "filas": filas,
    }


# ---------------------------------------------------------------------------
# Resumen para dirección (KPIs)
# ---------------------------------------------------------------------------
@router.get("/resumen-direccion")
def resumen_direccion(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Indicadores reales para el panel de dirección."""
    from app.models.incidents import Justificante

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    total_activos = (
        db.query(Empleado)
        .filter(Empleado.estado == "activo")
        .filter(Empleado.eliminado_en.is_(None))
        .count()
    )
    incidencias_hoy = (
        db.query(Incidencia).filter(Incidencia.fecha == hoy).count()
    )
    incidencias_mes = (
        db.query(Incidencia)
        .filter(Incidencia.fecha >= inicio_mes)
        .filter(Incidencia.fecha <= hoy)
        .count()
    )
    pendientes = (
        db.query(Incidencia).filter(Incidencia.estado == "pendiente").count()
    )
    justificantes_pendientes = (
        db.query(Justificante)
        .filter(Justificante.estado == "pendiente")
        .count()
    )
    periodos_abiertos = (
        db.query(PeriodoNomina).filter(PeriodoNomina.estado == "abierto").count()
    )
    retardos_hoy = (
        db.query(Incidencia)
        .filter(Incidencia.fecha == hoy)
        .filter(Incidencia.tipo_incidencia == "retardo")
        .count()
    )
    faltas_hoy = (
        db.query(Incidencia)
        .filter(Incidencia.fecha == hoy)
        .filter(Incidencia.tipo_incidencia == "falta")
        .count()
    )

    return {
        "fecha": str(hoy),
        "total_empleados_activos": total_activos,
        "incidencias_hoy": incidencias_hoy,
        "incidencias_mes": incidencias_mes,
        "incidencias_pendientes": pendientes,
        "retardos_hoy": retardos_hoy,
        "faltas_hoy": faltas_hoy,
        "justificantes_pendientes": justificantes_pendientes,
        "periodos_nomina_abiertos": periodos_abiertos,
        "mensaje": "Indicadores calculados a partir de datos reales de la base de datos.",
    }
