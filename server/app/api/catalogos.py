"""Endpoints de catálogos: departamentos, puestos, horarios."""

from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.repositories import (
    departamento_repo, puesto_repo, horario_repo,
)
from app.models.catalogs import Departamento, Puesto, Horario
from app.models.catalogs import AsignacionHorario
from app.models.employees import Empleado
from app.api.crud import crud_router
from app.schemas import (
    DepartamentoCreate, DepartamentoOut,
    PuestoCreate, PuestoOut,
    HorarioCreate, HorarioOut,
)
from app.services.auth import escribir_auditoria

router = APIRouter(prefix="/api/v1/catalogos", tags=["Catálogos"])

router_departamentos = crud_router(
    prefix="/departamentos",
    tags=["Departamentos"],
    model=Departamento,
    repo=departamento_repo,
    create_schema=DepartamentoCreate,
    update_schema=DepartamentoCreate,
    out_schema=DepartamentoOut,
    permiso_leer="usuarios.leer",
    permiso_escribir="usuarios.escribir",
    entidad="departamento",
    id_label="id",
)

router_puestos = crud_router(
    prefix="/puestos",
    tags=["Puestos"],
    model=Puesto,
    repo=puesto_repo,
    create_schema=PuestoCreate,
    update_schema=PuestoCreate,
    out_schema=PuestoOut,
    permiso_leer="usuarios.leer",
    permiso_escribir="usuarios.escribir",
    entidad="puesto",
    id_label="id",
)

router_horarios = crud_router(
    prefix="/horarios",
    tags=["Horarios"],
    model=Horario,
    repo=horario_repo,
    create_schema=HorarioCreate,
    update_schema=HorarioCreate,
    out_schema=HorarioOut,
    permiso_leer="usuarios.leer",
    permiso_escribir="usuarios.escribir",
    entidad="horario",
    id_label="id",
)

# Incluir sub-routers en el router principal de catálogos
router.include_router(router_departamentos)
router.include_router(router_puestos)
router.include_router(router_horarios)

__all__ = ["router"]
