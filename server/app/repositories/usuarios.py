"""Repositorio de usuarios."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.security import Usuario
from app.repositories.base import BaseRepository
from app.schemas import UsuarioCreate, UsuarioUpdate


class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def get_por_username(self, db: Session, *, username: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.username == username).first()

    def get_por_email(self, db: Session, *, email: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.email == email).first()

    def username_existe(self, db: Session, *, username: str) -> bool:
        return db.query(Usuario).filter(Usuario.username == username).first() is not None

    def email_existe(self, db: Session, *, email: str) -> bool:
        return db.query(Usuario).filter(Usuario.email == email).first() is not None

    def actualizar_intentos_fallidos(
        self, db: Session, *, usuario: Usuario, intentos: int, bloqueado_hasta=None
    ) -> Usuario:
        usuario.intentos_fallidos = intentos
        if bloqueado_hasta is not None:
            usuario.bloqueado_hasta = bloqueado_hasta
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def resetear_intentos_fallidos(self, db: Session, *, usuario: Usuario) -> Usuario:
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario


usuario_repo = UsuarioRepository(Usuario)
