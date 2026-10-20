"""Servicio de registro de asistencia y motor de incidencias.

Implementa la detección de retardos, faltas y otros eventos, junto con
ajustes auditables. Todas las reglas son configurables y no están hardcodeadas.
"""

from datetime import datetime, time, date, timedelta, timezone
from typing import Optional, List, Dict, Any
import json

from sqlalchemy.orm import Session

from app.models.attendance import EventoAsistencia, AjusteAsistencia, DispositivoRegistro
from app.models.incidents import Incidencia
from app.models.employees import Empleado
from app.models.catalogs import Horario, AsignacionHorario, DiaFestivo, DiaDescanso, CalendarioLaboral
from app.models.security import Usuario, Auditoria
from app.repositories import (
    evento_asistencia_repo, ajuste_asistencia_repo, dispositivo_repo,
    incidencia_repo, horario_repo, asignacion_horario_repo, empleado_repo,
)
from app.services.auth import escribir_auditoria


# ---------------------------------------------------------------- utilidades

def _obtener_horario_vigente(db: Session, empleado_id, fecha_hora: datetime) -> Optional[Horario]:
    """Obtiene el horario asignado vigente del empleado en la fecha dada."""
    asignaciones = (
        db.query(AsignacionHorario)
        .filter(AsignacionHorario.empleado_id == empleado_id)
        .filter(AsignacionHorario.fecha_inicio_vigencia <= fecha_hora.date())
        .filter(
            (AsignacionHorario.fecha_fin_vigencia.is_(None))
            | (AsignacionHorario.fecha_fin_vigencia >= fecha_hora.date())
        )
        .all()
    )
    for asignacion in asignaciones:
        horario = horario_repo.get(db, asignacion.horario_id)
        if horario and horario.activo:
            return horario
    return None


def _es_dia_laborable(db: Session, horario: Horario, fecha: date) -> bool:
    """Determina si la fecha es día laborable según el calendario y el horario."""
    try:
        dias = json.loads(horario.dias_laborables)
    except Exception:
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
    # date.weekday(): 0=lunes, 6=domingo
    nombres = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dia_semana = nombres[fecha.weekday()]
    if dia_semana not in dias:
        return False
    # Festivos: no laborables
    festivo = (
        db.query(DiaFestivo)
        .filter(DiaFestivo.fecha == fecha)
        .first()
    )
    if festivo:
        return False
    return True


def _detectar_duplicado_imposible(
    db: Session, *, empleado_id, tipo_evento: str, fecha_hora: datetime,
    excluir_evento_id=None
) -> str:
    """Devuelve 'valido', 'duplicado' o 'imposible'."""
    mismo_minuto = fecha_hora.replace(second=0, microsecond=0)
    q = db.query(EventoAsistencia).filter(
        EventoAsistencia.empleado_id == empleado_id,
        EventoAsistencia.fecha_hora == mismo_minuto,
    )
    if excluir_evento_id:
        q = q.filter(EventoAsistencia.id != excluir_evento_id)
    if q.first():
        return "duplicado"

    # Evento imposible: salida sin entrada previa el mismo día
    if tipo_evento == "salida":
        inicio_dia = fecha_hora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        entrada_prev = (
            db.query(EventoAsistencia)
            .filter(EventoAsistencia.empleado_id == empleado_id)
            .filter(EventoAsistencia.tipo_evento == "entrada")
            .filter(EventoAsistencia.fecha_hora >= inicio_dia)
            .filter(EventoAsistencia.fecha_hora < fin_dia)
            .filter(EventoAsistencia.fecha_hora < fecha_hora)
            .order_by(EventoAsistencia.fecha_hora.desc())
            .first()
        )
        if not entrada_prev:
            return "imposible"

    return "valido"


# ---------------------------------------------------------------- motor de incidencias

def calcular_incidencia_para_entrada(
    db: Session, *, empleado: Empleado, evento: EventoAsistencia
) -> Optional[Dict[str, Any]]:
    """Calcula si una entrada genera incidencia de retardo.

    Regla de tolerancia: configurable por horario (tolerancia_minutos).
    Documentación: el minuto límite se considera FUERA de tolerancia
    (valor provisional: 10 minutos, minuto 11 es retardo).
    """
    horario = _obtener_horario_vigente(db, empleado.id, evento.fecha_hora)
    if not horario:
        return None

    if not _es_dia_laborable(db, horario, evento.fecha_hora.date()):
        return None

    hora_entrada = horario.hora_entrada
    hora_real = evento.fecha_hora.time()
    tolerancia = timedelta(minutes=horario.tolerancia_minutos or 10)

    limite = (
        datetime.combine(evento.fecha_hora.date(), hora_entrada) + tolerancia
    ).time()

    if hora_real <= limite:
        return None  # dentro de tolerancia

    minutos_retardo = int(
        (
            datetime.combine(evento.fecha_hora.date(), hora_real)
            - datetime.combine(evento.fecha_hora.date(), hora_entrada)
        ).total_seconds()
        // 60
    )

    return {
        "tipo_incidencia": "retardo",
        "minutos_retardo": minutos_retardo,
        "tiempo_incidencia_minutos": minutos_retardo,
        "regla_aplicada": f"Retardo: entrada {hora_real} supera horario {hora_entrada} + tolerancia {horario.tolerancia_minutos} min",
        "justificada": False,
    }


def contar_retardos_periodo(
    db: Session, *, empleado_id, fecha_inicio: date, fecha_fin: date
) -> int:
    """Cuenta retardos del empleado en el periodo (para regla 3 retardos = 1 falta)."""
    return (
        db.query(Incidencia)
        .filter(Incidencia.empleado_id == empleado_id)
        .filter(Incidencia.tipo_incidencia == "retardo")
        .filter(Incidencia.fecha >= fecha_inicio)
        .filter(Incidencia.fecha <= fecha_fin)
        .filter(Incidencia.justificada.is_(False))
        .count()
    )


# ---------------------------------------------------------------- registro de evento

def registrar_evento(
    db: Session,
    *,
    empleado_id,
    tipo_evento: str,
    fecha_hora: datetime,
    metodo_registro: str,
    usuario: Optional[Usuario] = None,
    dispositivo_id=None,
    observaciones: Optional[str] = None,
) -> EventoAsistencia:
    """Registra un evento de asistencia, detecta anomalías y calcula incidencias."""
    empleado = empleado_repo.get(db, empleado_id)
    if not empleado:
        raise ValueError("Empleado no encontrado.")
    if empleado.estado != "activo":
        raise ValueError("El empleado no está activo.")

    resultado = _detectar_duplicado_imposible(
        db, empleado_id=empleado_id, tipo_evento=tipo_evento, fecha_hora=fecha_hora
    )

    evento = EventoAsistencia(
        empleado_id=empleado_id,
        dispositivo_id=dispositivo_id,
        tipo_evento=tipo_evento,
        fecha_hora=fecha_hora,
        metodo_registro=metodo_registro,
        resultado_validacion=resultado,
        observaciones=observaciones,
        usuario_registro_id=usuario.id if usuario else None,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    incidencia_datos = None
    if resultado == "valido" and tipo_evento == "entrada":
        incidencia_datos = calcular_incidencia_para_entrada(
            db, empleado=empleado, evento=evento
        )

    if incidencia_datos:
        incidencia = Incidencia(
            empleado_id=empleado_id,
            evento_asistencia_id=evento.id,
            fecha=evento.fecha_hora.date(),
            tipo_incidencia=incidencia_datos["tipo_incidencia"],
            minutos_retardo=incidencia_datos["minutos_retardo"],
            tiempo_incidencia_minutos=incidencia_datos["tiempo_incidencia_minutos"],
            regla_aplicada=incidencia_datos["regla_aplicada"],
            justificada=incidencia_datos["justificada"],
            estado="pendiente",
        )
        db.add(incidencia)
        evento.incidencia_detectada = True
        db.add(evento)
        db.commit()

    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="evento_asistencia",
        registro_id=str(evento.id),
        valor_nuevo=f"{tipo_evento} {fecha_hora} resultado={resultado}",
        motivo="Registro de asistencia",
        direccion_ip=None,
    )
    return evento


def corregir_evento(
    db: Session,
    *,
    evento_id,
    valor_corregido: dict,
    motivo: str,
    usuario: Usuario,
    aprobado_por=None,
) -> AjusteAsistencia:
    """Corrige un evento generando un ajuste auditable (valor anterior/nuevo)."""
    evento = evento_asistencia_repo.get(db, evento_id)
    if not evento:
        raise ValueError("Evento de asistencia no encontrado.")

    valor_anterior = {
        "tipo_evento": evento.tipo_evento,
        "fecha_hora": evento.fecha_hora.isoformat(),
        "observaciones": evento.observaciones,
    }

    ajuste = AjusteAsistencia(
        evento_asistencia_id=evento.id,
        valor_anterior=str(valor_anterior),
        valor_corregido=str(valor_corregido),
        motivo=motivo,
        fecha_ajuste=datetime.now(timezone.utc),
        usuario_responsable_id=usuario.id,
        aprobado_por_id=aprobado_por.id if aprobado_por else None,
        fecha_aprobacion=datetime.now(timezone.utc) if aprobado_por else None,
    )
    db.add(ajuste)

    if "tipo_evento" in valor_corregido:
        evento.tipo_evento = valor_corregido["tipo_evento"]
    if "fecha_hora" in valor_corregido:
        evento.fecha_hora = valor_corregido["fecha_hora"]
    if "observaciones" in valor_corregido:
        evento.observaciones = valor_corregido["observaciones"]

    db.add(evento)
    db.commit()
    db.refresh(ajuste)

    escribir_auditoria(
        db, usuario=usuario, operacion="ajustar", entidad="evento_asistencia",
        registro_id=str(evento.id),
        valor_anterior=str(valor_anterior),
        valor_nuevo=str(valor_corregido),
        motivo=motivo,
    )
    return ajuste


def listar_eventos_pendientes_salida(db: Session, *, dias: int = 30) -> List[EventoAsistencia]:
    """Devuelve entradas sin salida asociada en el rango de días (informativo)."""
    desde = datetime.now(timezone.utc) - timedelta(days=dias)
    entradas = (
        db.query(EventoAsistencia)
        .filter(EventoAsistencia.tipo_evento == "entrada")
        .filter(EventoAsistencia.fecha_hora >= desde)
        .all()
    )
    pendientes = []
    for entrada in entradas:
        fin_dia = entrada.fecha_hora.replace(hour=23, minute=59, second=59)
        salida = (
            db.query(EventoAsistencia)
            .filter(EventoAsistencia.empleado_id == entrada.empleado_id)
            .filter(EventoAsistencia.tipo_evento == "salida")
            .filter(EventoAsistencia.fecha_hora >= entrada.fecha_hora)
            .filter(EventoAsistencia.fecha_hora <= fin_dia)
            .first()
        )
        if not salida:
            pendientes.append(entrada)
    return pendientes
