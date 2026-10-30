"""Servicio de generación de datos de demostración.

Permite poblar rápidamente el sistema con asistencias, faltas e incidencias
realistas para que la demostración de venta se vea completa y profesional.
Todo se genera sobre la base de datos SQLite local (sin servidor externo).
"""

from __future__ import annotations

import random
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attendance import EventoAsistencia
from app.models.incidents import Incidencia
from app.models.employees import Empleado
from app.models.catalogs import Horario, AsignacionHorario, DiaFestivo
from app.models.security import Usuario
from app.repositories import (
    evento_asistencia_repo, incidencia_repo, empleado_repo,
    horario_repo, asignacion_horario_repo, dispositivo_repo,
)
from app.services.asistencia import (
    registrar_evento, _obtener_horario_vigente, _es_dia_laborable,
    calcular_incidencia_para_entrada,
)


def _horario_empleado(db: Session, empleado: Empleado, fecha: date) -> Horario | None:
    asignaciones = (
        db.query(AsignacionHorario)
        .filter(AsignacionHorario.empleado_id == empleado.id)
        .filter(AsignacionHorario.fecha_inicio_vigencia <= fecha)
        .filter(
            (AsignacionHorario.fecha_fin_vigencia.is_(None))
            | (AsignacionHorario.fecha_fin_vigencia >= fecha)
        )
        .all()
    )
    for a in asignaciones:
        h = horario_repo.get(db, a.horario_id)
        if h and h.activo:
            return h
    return None


def generar_asistencias_demo(
    db: Session,
    *,
    dias_atras: int = 5,
    usuario: Usuario | None = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Genera asistencias realistas para todos los empleados activos en los
    últimos `dias_atras` días (excluyendo fines de semana y festivos).

    Cada empleado marca entrada y salida con variaciones aleatorias dentro de
    su horario, generando retardos, salidas tempranas y entradas válidas de
    forma natural para la demostración.
    """
    random.seed(seed)
    empleados = (
        db.query(Empleado)
        .filter(Empleado.estado == "activo")
        .filter(Empleado.eliminado_en.is_(None))
        .all()
    )

    hoy = date.today()
    eventos_creados = 0
    incidencias_creadas = 0

    for empleado in empleados:
        for i in range(1, dias_atras + 1):
            fecha = hoy - timedelta(days=i)
            # Saltar fines de semana y festivos
            if fecha.weekday() >= 5:
                continue
            festivo = (
                db.query(DiaFestivo)
                .filter(DiaFestivo.fecha == fecha)
                .first()
            )
            if festivo:
                continue

            horario = _horario_empleado(db, empleado, fecha)
            if not horario:
                continue

            # 90% de probabilidad de asistir (10% falta justificada o no)
            if random.random() < 0.10:
                # Falta (sin eventos)
                existe_falta = (
                    db.query(Incidencia)
                    .filter(Incidencia.empleado_id == empleado.id)
                    .filter(Incidencia.fecha == fecha)
                    .filter(Incidencia.tipo_incidencia == "falta")
                    .first()
                )
                if not existe_falta:
                    inc = Incidencia(
                        empleado_id=empleado.id,
                        fecha=fecha,
                        tipo_incidencia="falta",
                        minutos_retardo=0,
                        tiempo_incidencia_minutos=480,
                        regla_aplicada="Falta: sin registro de entrada en día laborable",
                        justificada=random.random() < 0.4,
                        estado="pendiente",
                    )
                    db.add(inc)
                    incidencias_creadas += 1
                continue

            # Entrada: variación entre -5 min y +25 min respecto a la entrada
            minuto_entrada_var = random.randint(-5, 25)
            hora_entrada_dt = datetime.combine(fecha, horario.hora_entrada) + timedelta(
                minutes=minuto_entrada_var
            )
            # Evitar hora antes de las 5am
            if hora_entrada_dt.hour < 5:
                hora_entrada_dt = hora_entrada_dt.replace(hour=5, minute=0)

            evento_entrada = registrar_evento(
                db,
                empleado_id=empleado.id,
                tipo_evento="entrada",
                fecha_hora=hora_entrada_dt.replace(tzinfo=timezone.utc),
                metodo_registro="simulador",
                usuario=usuario,
                observaciones="Demo: entrada simulada",
            )
            eventos_creados += 1

            # Salida: variación entre -30 min y +15 min respecto a la salida
            minuto_salida_var = random.randint(-30, 15)
            hora_salida_dt = datetime.combine(fecha, horario.hora_salida) + timedelta(
                minutes=minuto_salida_var
            )
            # Asegurar que la salida sea después de la entrada
            if hora_salida_dt <= hora_entrada_dt:
                hora_salida_dt = hora_entrada_dt + timedelta(hours=4)

            evento_salida = registrar_evento(
                db,
                empleado_id=empleado.id,
                tipo_evento="salida",
                fecha_hora=hora_salida_dt.replace(tzinfo=timezone.utc),
                metodo_registro="simulador",
                usuario=usuario,
                observaciones="Demo: salida simulada",
            )
            eventos_creados += 1

    db.commit()
    return {
        "eventos_creados": eventos_creados,
        "incidencias_creadas": incidencias_creadas,
        "empleados": len(empleados),
        "dias": dias_atras,
    }


def generar_faltas_automaticas(
    db: Session,
    *,
    fecha: date | None = None,
    usuario: Usuario | None = None,
) -> Dict[str, Any]:
    """Genera incidencias de tipo 'falta' para empleados activos que no
    tienen entrada registrada en la fecha indicada (por defecto ayer)."""
    if fecha is None:
        fecha = date.today() - timedelta(days=1)

    empleados = (
        db.query(Empleado)
        .filter(Empleado.estado == "activo")
        .filter(Empleado.eliminado_en.is_(None))
        .all()
    )

    creadas = 0
    ya_tienen = 0
    sin_horario = 0

    inicio = datetime.combine(fecha, datetime.min.time()).replace(tzinfo=timezone.utc)
    fin = datetime.combine(fecha, datetime.max.time()).replace(tzinfo=timezone.utc)

    for emp in empleados:
        # ¿Ya tiene entrada ese día?
        tiene_entrada = (
            db.query(EventoAsistencia)
            .filter(EventoAsistencia.empleado_id == emp.id)
            .filter(EventoAsistencia.tipo_evento == "entrada")
            .filter(EventoAsistencia.fecha_hora >= inicio)
            .filter(EventoAsistencia.fecha_hora <= fin)
            .first()
        )
        if tiene_entrada:
            ya_tienen += 1
            continue

        # ¿Es día laborable para su horario?
        horario = _horario_empleado(db, emp, fecha)
        if not horario or not _es_dia_laborable(db, horario, fecha):
            sin_horario += 1
            continue

        # ¿Ya tiene incidencia de falta ese día?
        ya_falta = (
            db.query(Incidencia)
            .filter(Incidencia.empleado_id == emp.id)
            .filter(Incidencia.fecha == fecha)
            .filter(Incidencia.tipo_incidencia == "falta")
            .first()
        )
        if ya_falta:
            ya_tienen += 1
            continue

        inc = Incidencia(
            empleado_id=emp.id,
            fecha=fecha,
            tipo_incidencia="falta",
            minutos_retardo=0,
            tiempo_incidencia_minutos=480,
            regla_aplicada=(
                f"Falta automática: sin entrada registrada el {fecha} "
                f"(horario {horario.codigo})"
            ),
            justificada=False,
            estado="pendiente",
        )
        db.add(inc)
        creadas += 1

    db.commit()
    return {
        "fecha": str(fecha),
        "faltas_creadas": creadas,
        "empleados_con_entrada": ya_tienen,
        "sin_horario_laborable": sin_horario,
        "total_empleados": len(empleados),
    }


def limpiar_datos_demo(db: Session) -> Dict[str, int]:
    """Elimina eventos de asistencia e incidencias generadas en modo demo
    (mantiene empleados, usuarios, departamentos y horarios)."""
    eventos = db.query(EventoAsistencia).delete()
    incidencias = db.query(Incidencia).delete()
    db.commit()
    return {"eventos_eliminados": eventos, "incidencias_eliminadas": incidencias}
