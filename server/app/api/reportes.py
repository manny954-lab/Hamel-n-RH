"""Endpoints de reportes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


@router.get("/quincenal")
def reporte_quincenal(
    fecha_inicio: str,
    fecha_fin: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Reporte quincenal de asistencia (datos reales de la base de datos)."""
    from app.models.employees import Empleado
    from app.models.incidents import Incidencia

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
            "justificada": inc.justificada,
            "estado": inc.estado,
            "regla_aplicada": inc.regla_aplicada,
        })
    return {"periodo": {"inicio": fecha_inicio, "fin": fecha_fin}, "total": len(filas), "filas": filas}


@router.get("/resumen-direccion")
def resumen_direccion(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("reportes.leer")),
):
    """Indicadores reales para el panel de dirección."""
    from app.models.employees import Empleado
    from app.models.incidents import Incidencia
    from app.models.payroll import PeriodoNomina
    from datetime import date

    hoy = date.today()
    total_activos = db.query(Empleado).filter(Empleado.estado == "activo").count()
    incidencias_hoy = (
        db.query(Incidencia)
        .filter(Incidencia.fecha == hoy)
        .count()
    )
    pendientes = (
        db.query(Incidencia)
        .filter(Incidencia.estado == "pendiente")
        .count()
    )
    justificantes_pendientes = (
        db.query(__import__("app.models.incidents", fromlist=["Justificante"]).Justificante)
        .filter(__import__("app.models.incidents", fromlist=["Justificante"]).Justificante.estado == "pendiente")
        .count()
    )
    periodos_abiertos = (
        db.query(PeriodoNomina)
        .filter(PeriodoNomina.estado == "abierto")
        .count()
    )
    return {
        "fecha": str(hoy),
        "total_empleados_activos": total_activos,
        "incidencias_hoy": incidencias_hoy,
        "incidencias_pendientes": pendientes,
        "justificantes_pendientes": justificantes_pendientes,
        "periodos_nomina_abiertos": periodos_abiertos,
        "mensaje": "Indicadores calculados a partir de datos reales de la base de datos.",
    }
