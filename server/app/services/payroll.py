"""Servicio de control de nómina y prenómina.

La prenómina es revisable y no sustituye procesos oficiales de nómina.
No se aplican descuentos automáticos sin autorización humana.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session

from sqlalchemy import func

from app.models.payroll import (
    PeriodoNomina, ConceptoNomina, PropuestaAjuste, ResultadoNomina,
)
from app.models.employees import Empleado, ConfiguracionSalarial
from app.models.incidents import Incidencia
from app.models.security import Usuario
from app.repositories import (
    periodo_nomina_repo, concepto_nomina_repo, propuesta_ajuste_repo,
    resultado_nomina_repo, empleado_repo,
)
from app.services.auth import escribir_auditoria


def crear_periodo(db: Session, *, datos: dict, usuario: Usuario) -> PeriodoNomina:
    fecha_inicio = datos["fecha_inicio"]
    fecha_fin = datos["fecha_fin"]
    if isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)
    if isinstance(fecha_fin, str):
        fecha_fin = date.fromisoformat(fecha_fin)
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha fin no puede ser anterior a la fecha inicio.")

    # Validar solapamiento con periodos existentes
    solapado = (
        db.query(PeriodoNomina)
        .filter(PeriodoNomina.fecha_inicio <= fecha_fin)
        .filter(PeriodoNomina.fecha_fin >= fecha_inicio)
        .first()
    )
    if solapado:
        raise ValueError("El periodo se solapa con otro periodo existente.")

    periodo = PeriodoNomina(
        nombre=datos["nombre"],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="abierto",
    )
    db.add(periodo)
    db.commit()
    db.refresh(periodo)

    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="periodo_nomina",
        registro_id=str(periodo.id),
        valor_nuevo=f"{periodo.nombre} {fecha_inicio} a {fecha_fin}",
        motivo="Apertura de periodo de nómina",
    )
    return periodo


def calcular_prenomina(
    db: Session, *, periodo_id: UUID, usuario: Usuario
) -> List[ResultadoNomina]:
    """Calcula la prenómina de todos los empleados activos en el periodo.

    Muestra el cálculo paso a paso. No aplica descuentos automáticos.
    """
    periodo = periodo_nomina_repo.get(db, periodo_id)
    if not periodo:
        raise ValueError("Periodo de nómina no encontrado.")
    if periodo.estado != "abierto":
        raise ValueError("Solo se puede calcular prenómina en periodos abiertos.")

    empleados = (
        db.query(Empleado)
        .filter(Empleado.estado == "activo")
        .filter(Empleado.eliminado_en.is_(None))
        .all()
    )

    resultados: List[ResultadoNomina] = []
    for empleado in empleados:
        # Sueldo base vigente en el periodo
        vigente = (
            db.query(ConfiguracionSalarial)
            .filter(ConfiguracionSalarial.empleado_id == empleado.id)
            .filter(ConfiguracionSalarial.fecha_vigencia <= periodo.fecha_fin)
            .filter(
                (ConfiguracionSalarial.fecha_fin_vigencia.is_(None))
                | (ConfiguracionSalarial.fecha_fin_vigencia >= periodo.fecha_inicio)
            )
            .order_by(ConfiguracionSalarial.fecha_vigencia.desc())
            .first()
        )
        sueldo_base = vigente.sueldo_base if vigente else 0.0

        # Incidencias del periodo
        incidencias = (
            db.query(Incidencia)
            .filter(Incidencia.empleado_id == empleado.id)
            .filter(Incidencia.fecha >= periodo.fecha_inicio)
            .filter(Incidencia.fecha <= periodo.fecha_fin)
            .all()
        )
        faltas = [i for i in incidencias if i.tipo_incidencia == "falta"]
        retardos = [i for i in incidencias if i.tipo_incidencia == "retardo"]
        faltas_justificadas = [i for i in faltas if i.justificada]
        minutos_retardo = sum(i.minutos_retardo for i in retardos)

        # Días asistidos aproximados (días con evento de entrada válido)
        from app.models.attendance import EventoAsistencia
        desde = datetime.combine(periodo.fecha_inicio, datetime.min.time()).replace(tzinfo=timezone.utc)
        hasta = datetime.combine(periodo.fecha_fin, datetime.max.time()).replace(tzinfo=timezone.utc)
        dias_asistidos = (
            db.query(func.count(func.distinct(func.date(EventoAsistencia.fecha_hora))))
            .filter(EventoAsistencia.empleado_id == empleado.id)
            .filter(EventoAsistencia.tipo_evento == "entrada")
            .filter(EventoAsistencia.resultado_validacion == "valido")
            .filter(EventoAsistencia.fecha_hora >= desde)
            .filter(EventoAsistencia.fecha_hora <= hasta)
            .scalar()
        ) or 0

        total_preliminar = sueldo_base  # Sin descuentos automáticos

        resultado = ResultadoNomina(
            periodo_nomina_id=periodo_id,
            empleado_id=empleado.id,
            sueldo_base_periodo=sueldo_base,
            dias_laborables=0,  # pendiente de calendario del cliente
            dias_asistidos=dias_asistidos,
            faltas_registradas=len(faltas),
            faltas_justificadas=len(faltas_justificadas),
            retardos=len(retardos),
            minutos_retardo_acumulados=minutos_retardo,
            ajustes_propuestos=0.0,
            ajustes_aprobados=0.0,
            total_percepciones=sueldo_base,
            total_preliminar=total_preliminar,
            estado_aprobacion="pendiente",
            fecha_calculo=datetime.now(timezone.utc),
        )
        db.add(resultado)
        resultados.append(resultado)

    db.commit()
    for r in resultados:
        db.refresh(r)

    escribir_auditoria(
        db, usuario=usuario, operacion="calcular", entidad="prenomina",
        registro_id=str(periodo_id),
        valor_nuevo=f"{len(resultados)} empleados calculados",
        motivo="Cálculo de prenómina revisable",
    )
    return resultados


def proponer_ajuste(
    db: Session, *, datos: dict, usuario: Usuario
) -> PropuestaAjuste:
    propuesta = PropuestaAjuste(
        periodo_nomina_id=datos["periodo_nomina_id"],
        empleado_id=datos["empleado_id"],
        concepto_id=datos["concepto_id"],
        importe=datos["importe"],
        motivo=datos["motivo"],
        estado="propuesto",
        usuario_propuesta_id=usuario.id,
        fecha_propuesta=datetime.now(timezone.utc),
    )
    db.add(propuesta)
    db.commit()
    db.refresh(propuesta)

    escribir_auditoria(
        db, usuario=usuario, operacion="proponer", entidad="propuesta_ajuste",
        registro_id=str(propuesta.id),
        valor_nuevo=f"{datos['importe']} - {datos['motivo']}",
        motivo="Propuesta de ajuste de prenómina",
    )
    return propuesta


def decidir_propuesta_ajuste(
    db: Session, *, propuesta_id: UUID, estado: str, usuario: Usuario
) -> PropuestaAjuste:
    if estado not in ("aprobado", "rechazado"):
        raise ValueError("Estado debe ser 'aprobado' o 'rechazado'")
    propuesta = propuesta_ajuste_repo.get(db, propuesta_id)
    if not propuesta:
        raise ValueError("Propuesta no encontrada.")
    anterior = propuesta.estado
    propuesta.estado = estado
    propuesta.usuario_aprobacion_id = usuario.id
    propuesta.fecha_aprobacion = datetime.now(timezone.utc)
    db.add(propuesta)
    db.commit()
    db.refresh(propuesta)

    escribir_auditoria(
        db, usuario=usuario, operacion="decidir", entidad="propuesta_ajuste",
        registro_id=str(propuesta.id),
        valor_anterior=anterior,
        valor_nuevo=estado,
        motivo="Decisión sobre propuesta de ajuste",
    )
    return propuesta


def cerrar_periodo(
    db: Session, *, periodo_id: UUID, usuario: Usuario
) -> PeriodoNomina:
    periodo = periodo_nomina_repo.get(db, periodo_id)
    if not periodo:
        raise ValueError("Periodo no encontrado.")
    if periodo.estado == "cerrado":
        raise ValueError("El periodo ya está cerrado.")
    periodo.estado = "cerrado"
    periodo.fecha_cierre = datetime.now(timezone.utc)
    periodo.usuario_cierre_id = usuario.id
    db.add(periodo)
    db.commit()
    db.refresh(periodo)

    escribir_auditoria(
        db, usuario=usuario, operacion="cerrar", entidad="periodo_nomina",
        registro_id=str(periodo.id),
        valor_nuevo="cerrado",
        motivo="Cierre de periodo de nómina",
    )
    return periodo
