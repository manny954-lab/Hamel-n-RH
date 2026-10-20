"""Servicios de autenticación y gestión de sesiones."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import usuario_tiene_permiso
from app.models.security import Usuario, Sesion, Auditoria
from app.repositories.usuarios import usuario_repo
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def autenticar_usuario(db: Session, username: str, password: str) -> Optional[Usuario]:
    """Valida credenciales de usuario. Devuelve el usuario o None."""
    usuario = usuario_repo.get_por_username(db, username=username)
    if not usuario:
        return None
    if not usuario.activo:
        return None
    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.now(timezone.utc):
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario


def registrar_intento_fallido(db: Session, username: str) -> Optional[Usuario]:
    """Incrementa intentos fallidos y bloquea si se supera el límite."""
    from app.core.config import settings
    usuario = usuario_repo.get_por_username(db, username=username)
    if not usuario:
        return None
    intentos = usuario.intentos_fallidos + 1
    bloqueado = None
    if intentos >= settings.login_max_intentos:
        bloqueado = datetime.now(timezone.utc) + timedelta(minutes=settings.login_bloqueo_minutos)
    return usuario_repo.actualizar_intentos_fallidos(
        db, usuario=usuario, intentos=intentos, bloqueado_hasta=bloqueado
    )


def resetear_intentos_fallidos(db: Session, usuario: Usuario) -> Usuario:
    return usuario_repo.resetear_intentos_fallidos(db, usuario=usuario)


def crear_sesion(
    db: Session, usuario: Usuario, token_jti: str, expiracion: datetime,
    direccion_ip: Optional[str] = None, agente_usuario: Optional[str] = None
) -> Sesion:
    sesion = Sesion(
        usuario_id=usuario.id,
        token_jti=token_jti,
        fecha_expiracion=expiracion,
        direccion_ip=direccion_ip,
        agente_usuario=agente_usuario,
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion


def revocar_sesion(db: Session, token_jti: str) -> None:
    sesion = db.query(Sesion).filter(Sesion.token_jti == token_jti).first()
    if sesion and sesion.fecha_revocacion is None:
        sesion.fecha_revocacion = datetime.now(timezone.utc)
        db.add(sesion)
        db.commit()


def escribir_auditoria(
    db: Session,
    *,
    usuario: Optional[Usuario],
    operacion: str,
    entidad: str,
    registro_id: Optional[str] = None,
    valor_anterior: Optional[str] = None,
    valor_nuevo: Optional[str] = None,
    motivo: Optional[str] = None,
    resultado: str = "exito",
    direccion_ip: Optional[str] = None,
    detalles: Optional[str] = None,
) -> None:
    """Escribe un registro de auditoría. Nunca almacena contraseñas ni datos sensibles."""
    registro = Auditoria(
        usuario_id=usuario.id if usuario else None,
        fecha_hora=datetime.now(timezone.utc),
        operacion=operacion,
        entidad=entidad,
        registro_id=str(registro_id) if registro_id else None,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        motivo=motivo,
        resultado=resultado,
        direccion_ip=direccion_ip,
        detalles=detalles,
    )
    db.add(registro)
    db.commit()
