"""Utilidades de seguridad: hash de contraseñas (Argon2id) y tokens JWT.

Nunca se almacenan ni se transmiten contraseñas en texto plano.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid

from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.core.config import settings

# Contexto de hash con Argon2id (algoritmo seguro recomendado).
# Bcrypt se mantiene como fallback para compatibilidad con hashes existentes.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Genera el hash seguro de una contraseña usando Argon2id."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token de acceso JWT con identificador único (jti)."""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "jti": jti})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida un token JWT. Devuelve None si es inválido o expirado."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except InvalidTokenError:
        return None


def verificar_permiso(permisos_usuario: list, clave_permiso: str) -> bool:
    """Verifica si el usuario posee un permiso dado (lista de claves)."""
    return clave_permiso in permisos_usuario
