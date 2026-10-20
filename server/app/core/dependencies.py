"""Dependencias de autenticación y autorización para FastAPI."""

from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.security import Usuario, Rol
from app.repositories.usuarios import usuario_repo
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Usuario:
    """Obtiene el usuario autenticado a partir del token JWT."""
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de acceso no válidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credenciales_exception
        username: str = payload.get("sub")
        if username is None:
            raise credenciales_exception
    except InvalidTokenError:
        raise credenciales_exception

    usuario = usuario_repo.get_por_username(db, username=username)
    if usuario is None:
        raise credenciales_exception
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario desactivada",
        )
    return usuario


def usuario_tiene_permiso(usuario: Usuario, clave_permiso: str) -> bool:
    """Verifica si el usuario tiene un permiso a través de sus roles."""
    for rol in usuario.roles:
        if not rol.activo:
            continue
        for permiso in rol.permisos:
            if permiso.activo and permiso.clave == clave_permiso:
                return True
    return False


def requerir_permiso(clave_permiso: str):
    """Dependencia de FastAPI que exige un permiso específico."""

    def dependencia(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if not usuario_tiene_permiso(usuario, clave_permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permiso para realizar esta operación: {clave_permiso}",
            )
        return usuario

    return dependencia
