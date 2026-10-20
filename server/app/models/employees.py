"""Modelos de empleados y configuración salarial."""

import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin


class Empleado(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "empleados"

    numero_empleado: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    departamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    puesto_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("puestos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="activo", index=True)  # activo, baja_voluntaria, baja_involuntaria, licencia, suspendido

    usuario_creacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    usuario_modificacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    departamento: Mapped["Departamento"] = relationship(
        foreign_keys=[departamento_id], lazy="selectin"
    )
    puesto: Mapped[Optional["Puesto"]] = relationship(
        foreign_keys=[puesto_id], lazy="selectin"
    )
    asignaciones_horario: Mapped[List["AsignacionHorario"]] = relationship(
        back_populates="empleado", lazy="selectin"
    )
    configuracion_salarial: Mapped[List["ConfiguracionSalarial"]] = relationship(
        back_populates="empleado", lazy="selectin"
    )
    eventos_asistencia: Mapped[List["EventoAsistencia"]] = relationship(
        back_populates="empleado", lazy="selectin"
    )
    incidencias: Mapped[List["Incidencia"]] = relationship(
        back_populates="empleado", lazy="selectin"
    )
    justificantes: Mapped[List["Justificante"]] = relationship(
        back_populates="empleado", lazy="selectin"
    )


class ConfiguracionSalarial(Base, BaseModelMixin):
    __tablename__ = "configuracion_salarial"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sueldo_base: Mapped[float] = mapped_column(nullable=False)
    periodicidad: Mapped[str] = mapped_column(String(50), nullable=False)  # mensual, quincenal, semanal, hora
    fecha_vigencia: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin_vigencia: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    usuario_alta_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="configuracion_salarial", lazy="selectin")
