"""Endpoints de roles y permisos."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Rol, Permiso
from app.models.security import usuario_rol, rol_permiso
from sqlalchemy import select
from app.repositories import rol_repo, permiso_repo
from app.schemas import RolCreate, RolOut, PermisoOut
from app.services.auth import escribir_auditoria

router = APIRouter(prefix="/api/v1/roles", tags=["Roles y permisos"])


@router.get("", response_model=List[RolOut])
def listar_roles(
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.leer")),
):
    return rol_repo.get_multi(db)


@router.post("", response_model=RolOut, status_code=201)
def crear_rol(
    datos: RolCreate,
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.escribir")),
):
    if db.query(Rol).filter(Rol.nombre == datos.nombre).first():
        raise HTTPException(status_code=400, detail="El rol ya existe.")
    rol = Rol(nombre=datos.nombre, descripcion=datos.descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


@router.get("/{rol_id}/permisos", response_model=List[PermisoOut])
def permisos_de_rol(
    rol_id: UUID,
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.leer")),
):
    rol = rol_repo.get(db, rol_id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return [p for p in rol.permisos if p.activo]


@router.post("/{rol_id}/permisos/{permiso_id}")
def asignar_permiso_rol(
    rol_id: UUID,
    permiso_id: UUID,
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.escribir")),
):
    rol = rol_repo.get(db, rol_id)
    permiso = permiso_repo.get(db, permiso_id)
    if not rol or not permiso:
        raise HTTPException(status_code=404, detail="Rol o permiso no encontrado.")
    ya = db.execute(
        select(rol_permiso).where(
            rol_permiso.c.rol_id == rol_id,
            rol_permiso.c.permiso_id == permiso_id,
        )
    ).first()
    if not ya:
        db.execute(rol_permiso.insert().values(rol_id=rol_id, permiso_id=permiso_id))
        db.commit()
    return {"mensaje": "Permiso asignado al rol"}


@router.delete("/{rol_id}/permisos/{permiso_id}")
def quitar_permiso_rol(
    rol_id: UUID,
    permiso_id: UUID,
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.escribir")),
):
    db.execute(
        rol_permiso.delete().where(
            rol_permiso.c.rol_id == rol_id,
            rol_permiso.c.permiso_id == permiso_id,
        )
    )
    db.commit()
    return {"mensaje": "Permiso removido del rol"}


@router.post("/{usuario_id}/roles/{rol_id}")
def asignar_rol_usuario(
    usuario_id: UUID,
    rol_id: UUID,
    db: Session = Depends(get_db),
    _ = Depends(requerir_permiso("usuarios.escribir")),
):
    from app.models.security import Usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not usuario or not rol:
        raise HTTPException(status_code=404, detail="Usuario o rol no encontrado.")
    ya = db.execute(
        select(usuario_rol).where(
            usuario_rol.c.usuario_id == usuario_id,
            usuario_rol.c.rol_id == rol_id,
        )
    ).first()
    if not ya:
        db.execute(usuario_rol.insert().values(usuario_id=usuario_id, rol_id=rol_id))
        db.commit()
    return {"mensaje": "Rol asignado al usuario"}
