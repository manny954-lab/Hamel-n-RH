"""Pruebas de autenticación y seguridad."""

from datetime import datetime, timedelta, timezone

import pytest

from app.security import hash_password, verify_password, create_access_token, decode_token
from app.models.security import Usuario, Rol, Permiso
from app.repositories.usuarios import usuario_repo
from app.services.auth import (
    autenticar_usuario,
    registrar_intento_fallido,
    resetear_intentos_fallidos,
    escribir_auditoria,
)


def test_hash_y_verificar_password(db):
    hashed = hash_password("ContrasenaSegura2026!")
    assert verify_password("ContrasenaSegura2026!", hashed) is True
    assert verify_password("Incorrecta", hashed) is False


def test_crear_usuario_y_autenticar(db):
    usuario = Usuario(
        username="operador.test",
        nombre_completo="Operador Prueba",
        password_hash=hash_password("Clave1234!"),
        activo=True,
    )
    db.add(usuario)
    db.commit()

    autenticado = autenticar_usuario(db, "operador.test", "Clave1234!")
    assert autenticado is not None
    assert autenticado.username == "operador.test"

    assert autenticar_usuario(db, "operador.test", "mal") is None


def test_bloqueo_tras_intentos_fallidos(db):
    usuario = Usuario(
        username="bloqueado.test",
        nombre_completo="Bloqueo Prueba",
        password_hash=hash_password("Clave1234!"),
        activo=True,
        intentos_fallidos=0,
    )
    db.add(usuario)
    db.commit()

    from app.core.config import settings
    for _ in range(settings.login_max_intentos):
        registrar_intento_fallido(db, "bloqueado.test")

    db.refresh(usuario)
    assert usuario.bloqueado_hasta is not None
    assert autenticar_usuario(db, "bloqueado.test", "Clave1234!") is None

    resetear_intentos_fallidos(db, usuario)
    db.refresh(usuario)
    assert usuario.intentos_fallidos == 0
    assert usuario.bloqueado_hasta is None


def test_token_jwt(db):
    token = create_access_token({"sub": "usuario.test", "uid": "123"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "usuario.test"

    assert decode_token("token.invalido") is None


def test_escribir_auditoria_no_expone_credenciales(db):
    usuario = Usuario(
        username="auditor.test",
        nombre_completo="Auditor Prueba",
        password_hash=hash_password("Clave1234!"),
        activo=True,
    )
    db.add(usuario)
    db.commit()
    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="usuario",
        registro_id=str(usuario.id), motivo="prueba",
    )
    db.commit()

    from app.models.security import Auditoria
    registros = db.query(Auditoria).all()
    assert len(registros) >= 1
    # La auditoría nunca debe contener el hash de contraseña.
    for r in registros:
        assert "password" not in (r.detalles or "").lower()
        assert "hash" not in (r.valor_anterior or "").lower()
