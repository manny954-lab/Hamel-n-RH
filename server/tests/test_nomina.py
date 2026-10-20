"""Pruebas de cálculo de prenómina."""

from datetime import date, datetime, timedelta, timezone

import pytest

from app.models.catalogs import Departamento, Horario
from app.models.employees import Empleado, ConfiguracionSalarial
from app.models.security import Usuario
from app.models.payroll import PeriodoNomina, ResultadoNomina
from app.models.attendance import EventoAsistencia
from app.repositories import (
    departamento_repo, horario_repo, empleado_repo,
    configuracion_salarial_repo, periodo_nomina_repo,
)
from app.services.payroll import (
    crear_periodo, calcular_prenomina, proponer_ajuste,
    decidir_propuesta_ajuste, cerrar_periodo,
)
from app.services.asistencia import registrar_evento
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
    emp = Empleado(
        numero_empleado="0020", nombre="María", apellido_paterno="Díaz",
        departamento_id=depto.id, fecha_ingreso=date(2023, 1, 5), estado="activo",
    )
    db.add(emp)
    db.commit()
    db.refresh(depto); db.refresh(horario); db.refresh(emp)

    sal = ConfiguracionSalarial(
        empleado_id=emp.id, sueldo_base=16000.0, periodicidad="mensual",
        fecha_vigencia=date(2026, 1, 1),
    )
    db.add(sal)
    db.commit()
    return depto, horario, emp


def _asignar_horario(db, emp, horario):
    from app.models.catalogs import AsignacionHorario
    a = AsignacionHorario(
        empleado_id=emp.id, horario_id=horario.id,
        fecha_inicio_vigencia=date(2026, 1, 1),
    )
    db.add(a)
    db.commit()


def _usuario(db):
    u = Usuario(username="nomina.test", nombre_completo="Nómina Prueba", password_hash="x", activo=True)
    db.add(u); db.commit(); db.refresh(u)
    return u


def test_calcular_prenomina_sin_descuentos_automaticos(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = _usuario(db)

    # Entrada con retardo
    op = Usuario(username="op.test", nombre_completo="Op", password_hash="x", activo=True)
    db.add(op); db.commit(); db.refresh(op)
    registrar_evento(db, empleado_id=emp.id, tipo_evento="entrada",
                     fecha_hora=datetime(2026, 1, 12, 8, 20, 0),
                     metodo_registro="manual", usuario=op)

    periodo = crear_periodo(db, datos={
        "nombre": "Q1 2026", "fecha_inicio": date(2026, 1, 1),
        "fecha_fin": date(2026, 1, 15),
    }, usuario=usuario)

    resultados = calcular_prenomina(db, periodo_id=periodo.id, usuario=usuario)
    assert len(resultados) == 1
    r = resultados[0]
    assert r.retardos == 1
    assert r.minutos_retardo_acumulados == 20
    # Sin descuentos automáticos: total preliminar = sueldo base
    assert r.total_preliminar == 16000.0


def test_ajuste_propuesto_y_aprobado(db):
    _, horario, emp = _setup(db)
    _asignar_horario(db, emp, horario)
    usuario = _usuario(db)
    periodo = crear_periodo(db, datos={
        "nombre": "Q1 2026", "fecha_inicio": date(2026, 1, 1),
        "fecha_fin": date(2026, 1, 15),
    }, usuario=usuario)

    # Necesita un concepto de nómina
    from app.models.payroll import ConceptoNomina
    concepto = ConceptoNomina(clave="BONO", nombre="Bono puntualidad", tipo="percepcion", activo=True)
    db.add(concepto); db.commit(); db.refresh(concepto)

    propuesta = proponer_ajuste(db, datos={
        "periodo_nomina_id": periodo.id,
        "empleado_id": emp.id,
        "concepto_id": concepto.id,
        "importe": 500.0,
        "motivo": "Bono por asistencia puntual",
    }, usuario=usuario)
    assert propuesta.estado == "propuesto"
    assert propuesta.importe == 500.0

    aprobada = decidir_propuesta_ajuste(db, propuesta_id=propuesta.id, estado="aprobado", usuario=usuario)
    assert aprobada.estado == "aprobado"

    # Cierre de periodo
    cerrado = cerrar_periodo(db, periodo_id=periodo.id, usuario=usuario)
    assert cerrado.estado == "cerrado"

    # Reabrir no está implementado; cierre doble debe fallar
    from app.services.payroll import cerrar_periodo as cerrar2
    with pytest.raises(ValueError):
        cerrar2(db, periodo_id=periodo.id, usuario=usuario)
