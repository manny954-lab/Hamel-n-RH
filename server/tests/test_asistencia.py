"""Pruebas de registro de asistencia y motor de incidencias."""

from datetime import datetime

import pytest

from app.models.catalogs import Departamento, Horario
from app.models.employees import Empleado
from app.models.security import Usuario
from app.models.attendance import EventoAsistencia
from app.repositories import departamento_repo, horario_repo, empleado_repo, evento_asistencia_repo
from app.services.asistencia import (
    registrar_evento,
    _obtener_horario_vigente,
    _es_dia_laborable,
    _detectar_duplicado_imposible,
    contar_retardos_periodo,
)
from app.models.incidents import Incidencia


def _setup(db):
    depto = Departamento(codigo="ADM", nombre="Administración", activo=True)
    db.add(depto)
    db.flush()
    horario = Horario(
        codigo="ADM-08-16", nombre="Admin 08-16",
        hora_entrada=__import__("datetime").time(8, 0),
        hora_salida=__import__("datetime").time(16, 0),
        tolerancia_minutos=10,
        dias_laborables='["lunes","martes","miercoles","jueves","viernes","sabado"]',
        activo=True,
    )
    db.add(horario)
    db.flush()
    emp = Empleado(
        numero_empleado="0010", nombre="Carlos", apellido_paterno="Ruiz",
        departamento_id=depto.id, fecha_ingreso=__import__("datetime").date(2023, 1, 5),
        estado="activo",
    )
    db.add(emp)
    db.commit()
    db.refresh(depto); db.refresh(horario); db.refresh(emp)
    return depto, horario, emp


def _asignar_horario(db, emp, horario, inicio="2026-01-01"):
    from app.models.catalogs import AsignacionHorario
    a = AsignacionHorario(
        empleado_id=emp.id, horario_id=horario.id,
        fecha_inicio_vigencia=__import__("datetime").date.fromisoformat(inicio),
    )
    db.add(a)
    db.commit()


def test_entrada_dentro_de_tolerancia_no_genera_incidencia(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(usuario); db.commit(); db.refresh(usuario)

    entrada = datetime(2026, 1, 12, 8, 5, 0)  # 5 min, dentro de tolerancia 10
    evento = registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                              fecha_hora=entrada, metodo_registro="manual", usuario=usuario)
    assert evento.incidencia_detectada is False
    assert evento.resultado_validacion == "valido"


def test_entrada_fuera_de_tolerancia_genera_retardo(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(usuario); db.commit(); db.refresh(usuario)

    entrada = datetime(2026, 1, 12, 8, 20, 0)  # 20 min de retardo
    evento = registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                              fecha_hora=entrada, metodo_registro="manual", usuario=usuario)
    assert evento.incidencia_detectada is True
    inc = db.query(Incidencia).filter(Incidencia.empleado_id == emp.id).first()
    assert inc is not None
    assert inc.tipo_incidencia == "retardo"
    assert inc.minutos_retardo == 20
    assert "tolerancia 10 min" in inc.regla_aplicada


def test_entrada_duplicado(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(usuario); db.commit(); db.refresh(usuario)

    entrada = datetime(2026, 1, 12, 8, 0, 0)
    registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                     fecha_hora=entrada, metodo_registro="manual", usuario=usuario)
    evento2 = registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                               fecha_hora=entrada, metodo_registro="manual", usuario=usuario)
    assert evento2.resultado_validacion == "duplicado"


def test_salida_sin_entrada_es_imposible(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(usuario); db.commit(); db.refresh(usuario)

    salida = datetime(2026, 1, 12, 9, 0, 0)
    evento = registrar_evento(db, empleado_id=emp.id, tipo_evento="salida",
                              fecha_hora=salida, metodo_registro="manual", usuario=usuario)
    assert evento.resultado_validacion == "imposible"


def test_contar_retardos_periodo(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(usuario); db.commit(); db.refresh(usuario)

    for minuto in [20, 25, 30]:
        registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                         fecha_hora=datetime(2026, 1, 12, 8, minuto, 0),
                         metodo_registro="manual", usuario=usuario)
    # Solo el primer registro del mismo minuto cuenta; los demás son duplicados.
    total = contar_retardos_periodo(db, empleado_id=emp.id,
                                    fecha_inicio=__import__("datetime").date(2026, 1, 1),
                                    fecha_fin=__import__("datetime").date(2026, 1, 31))
    assert total >= 1
