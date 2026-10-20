"""Esquemas Pydantic para validación de datos de entrada y salida."""

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ==================== Autenticación ====================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    nombre_completo: str = Field(..., min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None


class UsuarioOut(UsuarioBase):
    id: UUID
    ultimo_acceso: Optional[datetime] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class CambioPassword(BaseModel):
    password_actual: str
    password_nueva: str = Field(..., min_length=8)


class RestablecerPassword(BaseModel):
    password_nueva: str = Field(..., min_length=8)


# ==================== Roles y permisos ====================

class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolCreate(RolBase):
    pass


class RolOut(RolBase):
    id: UUID
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class PermisoBase(BaseModel):
    clave: str
    descripcion: Optional[str] = None
    modulo: str


class PermisoOut(PermisoBase):
    id: UUID
    activo: bool

    class Config:
        from_attributes = True


# ==================== Departamentos ====================

class DepartamentoBase(BaseModel):
    codigo: str
    nombre: str
    activo: bool = True


class DepartamentoCreate(DepartamentoBase):
    pass


class DepartamentoOut(DepartamentoBase):
    id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== Puestos ====================

class PuestoBase(BaseModel):
    codigo: str
    nombre: str
    departamento_id: UUID
    activo: bool = True


class PuestoCreate(PuestoBase):
    pass


class PuestoOut(PuestoBase):
    id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== Horarios ====================

class HorarioBase(BaseModel):
    codigo: str
    nombre: str
    hora_entrada: time
    hora_salida: time
    cruza_medianoche: bool = False
    periodo_comida_minutos: int = 0
    dias_laborables: str = '["lunes","martes","miercoles","jueves","viernes","sabado"]'
    tolerancia_minutos: int = 10
    activo: bool = True


class HorarioCreate(HorarioBase):
    pass


class HorarioOut(HorarioBase):
    id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== Empleados ====================

class EmpleadoBase(BaseModel):
    numero_empleado: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    departamento_id: UUID
    puesto_id: Optional[UUID] = None
    fecha_ingreso: date  # YYYY-MM-DD
    estado: str = "activo"


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoOut(EmpleadoBase):
    id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== Eventos de asistencia ====================

class EventoAsistenciaBase(BaseModel):
    empleado_id: UUID
    tipo_evento: str  # entrada, salida, otro
    fecha_hora: datetime
    metodo_registro: str  # manual, biometrico, tarjeta, simulador
    observaciones: Optional[str] = None


class EventoAsistenciaCreate(EventoAsistenciaBase):
    dispositivo_id: Optional[UUID] = None


class EventoAsistenciaOut(EventoAsistenciaBase):
    id: UUID
    dispositivo_id: Optional[UUID] = None
    resultado_validacion: str
    incidencia_detectada: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== Incidencias ====================

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


# ==================== Justificantes ====================

class JustificanteBase(BaseModel):
    empleado_id: UUID
    tipo: str  # medico, legal, transito, otro
    fecha_incidencia: date  # YYYY-MM-DD
    descripcion: Optional[str] = None


class JustificanteCreate(JustificanteBase):
    pass


class JustificanteOut(JustificanteBase):
    id: UUID
    estado: str
    fecha_solicitud: datetime

    class Config:
        from_attributes = True


# ==================== Prenómina ====================

class PeriodoNominaBase(BaseModel):
    nombre: str
    fecha_inicio: date  # YYYY-MM-DD
    fecha_fin: date


class PeriodoNominaCreate(PeriodoNominaBase):
    pass


class PeriodoNominaOut(PeriodoNominaBase):
    id: UUID
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class PropuestaAjusteBase(BaseModel):
    periodo_nomina_id: UUID
    empleado_id: UUID
    concepto_id: UUID
    importe: float
    motivo: str


class PropuestaAjusteCreate(PropuestaAjusteBase):
    pass


class PropuestaAjusteOut(PropuestaAjusteBase):
    id: UUID
    estado: str
    fecha_propuesta: datetime

    class Config:
        from_attributes = True


# ==================== Auditoría ====================

class AuditoriaOut(BaseModel):
    id: UUID
    fecha_hora: datetime
    operacion: str
    entidad: str
    registro_id: Optional[str]
    resultado: str
    motivo: Optional[str]

    class Config:
        from_attributes = True
