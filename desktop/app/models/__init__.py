"""Modelos de intercambio de datos para la interfaz de escritorio."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    id: UUID
    username: str
    nombre_completo: str
    email: Optional[EmailStr] = None
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class DepartamentoOut(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    activo: bool

    class Config:
        from_attributes = True


class HorarioOut(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    hora_entrada: str
    hora_salida: str
    tolerancia_minutos: int
    activo: bool

    class Config:
        from_attributes = True


class EmpleadoOut(BaseModel):
    id: UUID
    numero_empleado: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    departamento_id: UUID
    puesto_id: Optional[UUID] = None
    fecha_ingreso: str
    estado: str

    class Config:
        from_attributes = True


class EventoAsistenciaOut(BaseModel):
    id: UUID
    empleado_id: UUID
    tipo_evento: str
    fecha_hora: datetime
    metodo_registro: str
    resultado_validacion: str
    incidencia_detectada: bool

    class Config:
        from_attributes = True


class IncidenciaOut(BaseModel):
    id: UUID
    empleado_id: UUID
    fecha: str
    tipo_incidencia: str
    minutos_retardo: int
    tiempo_incidencia_minutos: int
    regla_aplicada: str
    justificada: bool
    estado: str

    class Config:
        from_attributes = True


class JustificanteOut(BaseModel):
    id: UUID
    empleado_id: UUID
    tipo: str
    fecha_incidencia: str
    descripcion: Optional[str]
    estado: str
    fecha_solicitud: datetime

    class Config:
        from_attributes = True


class PeriodoNominaOut(BaseModel):
    id: UUID
    nombre: str
    fecha_inicio: str
    fecha_fin: str
    estado: str

    class Config:
        from_attributes = True


class ResultadoNominaOut(BaseModel):
    id: UUID
    empleado_id: UUID
    sueldo_base_periodo: float
    dias_laborables: int
    dias_asistidos: int
    faltas_registradas: int
    faltas_justificadas: int
    retardos: int
    minutos_retardo_acumulados: int
    ajustes_propuestos: float
    ajustes_aprobados: float
    total_percepciones: float
    total_preliminar: float
    estado_aprobacion: str

    class Config:
        from_attributes = True
