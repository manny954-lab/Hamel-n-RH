"""Modelos de registro de asistencia y dispositivos."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin


class DispositivoRegistro(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "dispositivos_registro"

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # software, lector_biometrico, terminal
    identificador_externo: Mapped[Optional[str]] = mapped_column(String(200), unique=True, nullable=True, index=True)
    ubicacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    eventos: Mapped[List["EventoAsistencia"]] = relationship(back_populates="dispositivo", lazy="selectin")


class EventoAsistencia(Base, BaseModelMixin):
    __tablename__ = "eventos_asistencia"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dispositivo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dispositivos_registro.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # entrada, salida, otro
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metodo_registro: Mapped[str] = mapped_column(String(50), nullable=False)  # manual, biometrico, tarjeta, simulador
    resultado_validacion: Mapped[str] = mapped_column(String(30), nullable=False, default="valido")  # valido, duplicado, imposible, pendiente
    incidencia_detectada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    usuario_registro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    empleado: Mapped["Empleado"] = relationship(back_populates="eventos_asistencia", lazy="selectin")
    dispositivo: Mapped[Optional["DispositivoRegistro"]] = relationship(back_populates="eventos", lazy="selectin")
    ajustes: Mapped[List["AjusteAsistencia"]] = relationship(back_populates="evento", lazy="selectin")
    incidencia: Mapped[Optional["Incidencia"]] = relationship(back_populates="evento_asistencia", uselist=False, lazy="selectin")


class AjusteAsistencia(Base, BaseModelMixin):
    __tablename__ = "ajustes_asistencia"

    evento_asistencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eventos_asistencia.id", ondelete="CASCADE"), nullable=False, index=True
    )
    valor_anterior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valor_corregido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    motivo: Mapped[str] = mapped_column(String(500), nullable=False)
    fecha_ajuste: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usuario_responsable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    fecha_aprobacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    evento: Mapped["EventoAsistencia"] = relationship(back_populates="ajustes", lazy="selectin")
