"""Modelos de notificaciones y prenómina."""

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin


class Notificacion(Base, BaseModelMixin):
    __tablename__ = "notificaciones"

    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    departamento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    tipo_incidencia: Mapped[str] = mapped_column(String(50), nullable=False)
    tiempo_detectado_minutos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estado_atencion: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente")  # pendiente, revisada, resuelta
    usuario_responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    fecha_resolucion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PeriodoNomina(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "periodos_nomina"

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="abierto", index=True)  # abierto, calculado, cerrado, reabierto
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usuario_cierre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ConceptoNomina(Base, BaseModelMixin, SoftDeleteMixin):
    __tablename__ = "conceptos_nomina"

    clave: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # percepcion, deduccion, ajuste
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requiere_validacion_legal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    observaciones_legal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PropuestaAjuste(Base, BaseModelMixin):
    __tablename__ = "propuestas_ajuste"

    periodo_nomina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("periodos_nomina.id", ondelete="CASCADE"), nullable=False, index=True
    )
    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    concepto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conceptos_nomina.id", ondelete="RESTRICT"), nullable=False
    )
    importe: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="propuesto", index=True)  # propuesto, aprobado, rechazado
    usuario_propuesta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    fecha_propuesta: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usuario_aprobacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    fecha_aprobacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ResultadoNomina(Base, BaseModelMixin):
    __tablename__ = "resultados_nomina"

    periodo_nomina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("periodos_nomina.id", ondelete="CASCADE"), nullable=False, index=True
    )
    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sueldo_base_periodo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    dias_laborables: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dias_asistidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    faltas_registradas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    faltas_justificadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retardos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    minutos_retardo_acumulados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ajustes_propuestos: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    ajustes_aprobados: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_percepciones: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_preliminar: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    estado_aprobacion: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente")  # pendiente, aprobado, rechazado
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        __import__("sqlalchemy").UniqueConstraint(
            "periodo_nomina_id", "empleado_id", name="uq_periodo_empleado_resultado"
        ),
    )
