"""Pruebas de gestión de empleados."""

from datetime import date

import pytest

from app.models.catalogs import Departamento
from app.models.employees import Empleado
from app.models.security import Usuario
from app.repositories import departamento_repo, empleado_repo
from app.services.empleados import (
    crear_empleado,
    actualizar_empleado,
    cambiar_estado_empleado,
    validar_empleado_data,
)


def _crear_departamento(db):
    d = Departamento(codigo="ADM", nombre="Administración", activo=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _crear_usuario(db):
    u = Usuario(username="rh.test", nombre_completo="RH Prueba", password_hash="x", activo=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_crear_empleado(db):
    depto = _crear_departamento(db)
    usuario = _crear_usuario(db)
    empleado = crear_empleado(db, datos={
        "numero_empleado": "0001",
        "nombre": "Ana",
        "apellido_paterno": "García",
        "apellido_materno": "López",
        "departamento_id": depto.id,
        "fecha_ingreso": date(2023, 1, 10),
        "estado": "activo",
    }, usuario=usuario)
    assert empleado.numero_empleado == "0001"
    assert empleado.departamento_id == depto.id


def test_numero_empleado_duplicado(db):
    depto = _crear_departamento(db)
    usuario = _crear_usuario(db)
    crear_empleado(db, datos={
        "numero_empleado": "0002", "nombre": "Ana", "apellido_paterno": "García",
        "departamento_id": depto.id, "fecha_ingreso": date(2023, 1, 10),
    }, usuario=usuario)
    with pytest.raises(ValueError, match="Ya existe"):
        crear_empleado(db, datos={
            "numero_empleado": "0002", "nombre": "Otro", "apellido_paterno": "X",
            "departamento_id": depto.id, "fecha_ingreso": date(2023, 1, 10),
        }, usuario=usuario)


def test_cambiar_estado_empleado(db):
    depto = _crear_departamento(db)
    usuario = _crear_usuario(db)
    empleado = crear_empleado(db, datos={
        "numero_empleado": "0003", "nombre": "Luis", "apellido_paterno": "Pérez",
        "departamento_id": depto.id, "fecha_ingreso": date(2023, 1, 10),
    }, usuario=usuario)
    actualizado = cambiar_estado_empleado(db, empleado_id=empleado.id, estado="licencia", usuario=usuario)
    assert actualizado.estado == "licencia"

    with pytest.raises(ValueError):
        cambiar_estado_empleado(db, empleado_id=empleado.id, estado="invalido", usuario=usuario)
