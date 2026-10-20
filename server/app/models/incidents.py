"""Modelos de incidencias y justificantes."""

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Incidencia(Base, BaseModelMixin):
    __tablename__ = "incidencias"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evento_asistencia_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eventos_asistencia.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    tipo_incidencia: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # retardo, falta, entrada_incompleta, salida_incompleta, salida_anticipada, horas_extras
    minutos_retardo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tiempo_incidencia_minutos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    regla_aplicada: Mapped[str] = mapped_column(String(255), nullable=False)
    justificada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justificante_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("justificantes.id", ondelete="SET NULL"), nullable=True
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente", index=True)  # pendiente, en_revision, aprobada, rechazada
    usuario_responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="incidencias", lazy="selectin")
    evento_asistencia: Mapped[Optional["EventoAsistencia"]] = relationship(
        back_populates="incidencia", lazy="selectin"
    )
    justificante: Mapped[Optional["Justificante"]] = relationship(back_populates="incidencias", lazy="selectin")


class Justificante(Base, BaseModelMixin):
    __tablename__ = "justificantes"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # medico, legal, transito, otro
    fecha_incidencia: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente", index=True)  # pendiente, en_revision, aprobada, rechazada, cancelada
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_decision: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usuario_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    documento_adjunto_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("archivos_adjuntos.id", ondelete="SET NULL"), nullable=True
    )

    empleado: Mapped["Empleado"] = relationship(back_populates="justificantes", lazy="selectin")
    incidencias: Mapped[List["Incidencia"]] = relationship(back_populates="justificante", lazy="selectin")
    documento_adjunto: Mapped[Optional["ArchivoAdjunto"]] = relationship(lazy="selectin")


class ArchivoAdjunto(Base, BaseModelMixin):
    __tablename__ = "archivos_adjuntos"

    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta_almacenamiento: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tamano_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_subida: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usuario_subida_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    acceso_restringido: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
