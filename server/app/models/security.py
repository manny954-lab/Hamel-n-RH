"""Modelos de seguridad y control de acceso."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin


# Tablas de asociación muchos a muchos (vinculadas a la metadata de Base)
usuario_rol = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", UUID(as_uuid=True), ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
)


class Usuario(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "usuarios"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    bloqueado_hasta: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    debe_cambiar_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[List["Rol"]] = relationship(
        secondary=usuario_rol, back_populates="usuarios", lazy="selectin"
    )
    sesiones: Mapped[List["Sesion"]] = relationship(back_populates="usuario", lazy="selectin")
    auditoria: Mapped[List["Auditoria"]] = relationship(back_populates="usuario", lazy="selectin")


class Rol(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "roles"

    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuarios: Mapped[List["Usuario"]] = relationship(
        secondary=usuario_rol, back_populates="roles", lazy="selectin"
    )
    permisos: Mapped[List["Permiso"]] = relationship(
        secondary=rol_permiso, back_populates="roles", lazy="selectin"
    )


class Permiso(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "permisos"

    clave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    modulo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    roles: Mapped[List["Rol"]] = relationship(
        secondary=rol_permiso, back_populates="permisos", lazy="selectin"
    )


class Sesion(Base, BaseModelMixin):
    __tablename__ = "sesiones"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_jti: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_revocacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    agente_usuario: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    usuario: Mapped["Usuario"] = relationship(back_populates="sesiones", lazy="selectin")


class Auditoria(Base, BaseModelMixin):
    __tablename__ = "auditoria"

    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    operacion: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entidad: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    registro_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    valor_anterior: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    valor_nuevo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    detalles: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    usuario: Mapped[Optional["Usuario"]] = relationship(back_populates="auditoria", lazy="selectin")
