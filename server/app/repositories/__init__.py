"""Repositorios de catálogos y seguridad."""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.security import Rol, Permiso
from app.models.catalogs import (
    Departamento, Puesto, Horario, AsignacionHorario,
    CalendarioLaboral, DiaFestivo, DiaDescanso, ConfiguracionGeneral,
)
from app.models.employees import Empleado, ConfiguracionSalarial
from app.models.attendance import (
    DispositivoRegistro, EventoAsistencia, AjusteAsistencia,
)
from app.models.incidents import Incidencia, Justificante, ArchivoAdjunto
from app.models.payroll import (
    PeriodoNomina, ConceptoNomina, PropuestaAjuste, ResultadoNomina, Notificacion,
)
from app.repositories.base import BaseRepository


rol_repo = BaseRepository(Rol)
permiso_repo = BaseRepository(Permiso)

departamento_repo = BaseRepository(Departamento)
puesto_repo = BaseRepository(Puesto)
horario_repo = BaseRepository(Horario)
asignacion_horario_repo = BaseRepository(AsignacionHorario)
calendario_repo = BaseRepository(CalendarioLaboral)
dia_festivo_repo = BaseRepository(DiaFestivo)
dia_descanso_repo = BaseRepository(DiaDescanso)
configuracion_general_repo = BaseRepository(ConfiguracionGeneral)

empleado_repo = BaseRepository(Empleado)
configuracion_salarial_repo = BaseRepository(ConfiguracionSalarial)

dispositivo_repo = BaseRepository(DispositivoRegistro)
evento_asistencia_repo = BaseRepository(EventoAsistencia)
ajuste_asistencia_repo = BaseRepository(AjusteAsistencia)

incidencia_repo = BaseRepository(Incidencia)
justificante_repo = BaseRepository(Justificante)
archivo_adjunto_repo = BaseRepository(ArchivoAdjunto)

notificacion_repo = BaseRepository(Notificacion)
periodo_nomina_repo = BaseRepository(PeriodoNomina)
concepto_nomina_repo = BaseRepository(ConceptoNomina)
propuesta_ajuste_repo = BaseRepository(PropuestaAjuste)
resultado_nomina_repo = BaseRepository(ResultadoNomina)
