"""Modelos de catálogos organizativos: departamentos, puestos, horarios, calendarios."""

import uuid
from datetime import date, time
from typing import List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin


class Departamento(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "departamentos"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    puestos: Mapped[List["Puesto"]] = relationship(back_populates="departamento", lazy="selectin")
    empleados: Mapped[List["Empleado"]] = relationship(back_populates="departamento", lazy="selectin")


class Puesto(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "puestos"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    departamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    departamento: Mapped["Departamento"] = relationship(back_populates="puestos", lazy="selectin")
    empleados: Mapped[List["Empleado"]] = relationship(back_populates="puesto", lazy="selectin")


class Horario(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "horarios"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    hora_entrada: Mapped[time] = mapped_column(Time, nullable=False)
    hora_salida: Mapped[time] = mapped_column(Time, nullable=False)
    cruza_medianoche: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodo_comida_minutos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dias_laborables: Mapped[str] = mapped_column(String(200), nullable=False)  # JSON como texto
    tolerancia_minutos: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    asignaciones: Mapped[List["AsignacionHorario"]] = relationship(
        back_populates="horario", lazy="selectin"
    )


class AsignacionHorario(Base, BaseModelMixin):
    __tablename__ = "asignaciones_horario"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    horario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("horarios.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    fecha_inicio_vigencia: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin_vigencia: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="asignaciones_horario", lazy="selectin")
    horario: Mapped["Horario"] = relationship(back_populates="asignaciones", lazy="selectin")


class CalendarioLaboral(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "calendarios_laborales"

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    festivos: Mapped[List["DiaFestivo"]] = relationship(back_populates="calendario", lazy="selectin")
    descansos: Mapped[List["DiaDescanso"]] = relationship(back_populates="calendario", lazy="selectin")


class DiaFestivo(Base, BaseModelMixin):
    __tablename__ = "dias_festivos"

    calendario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calendarios_laborales.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    __table_args__ = (UniqueConstraint("calendario_id", "fecha", name="uq_calendario_fecha_festivo"),)

    calendario: Mapped["CalendarioLaboral"] = relationship(back_populates="festivos", lazy="selectin")


class DiaDescanso(Base, BaseModelMixin):
    __tablename__ = "dias_descanso"

    calendario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calendarios_laborales.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=domingo ... 6=sabado

    __table_args__ = (UniqueConstraint("calendario_id", "dia_semana", name="uq_calendario_dia_descanso"),)

    calendario: Mapped["CalendarioLaboral"] = relationship(back_populates="descansos", lazy="selectin")


class ConfiguracionGeneral(Base, BaseModelMixin):
    __tablename__ = "configuracion_general"

    clave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    valor: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
