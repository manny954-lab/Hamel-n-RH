"""Endpoints de usuarios."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario
from app.repositories.usuarios import usuario_repo
from app.services.auth import escribir_auditoria
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get("", response_model=List[UsuarioOut])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("usuarios.leer")),
):
    return usuario_repo.get_multi(db, skip=skip, limit=limit)


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("usuarios.escribir")),
):
    if usuario_repo.username_existe(db, username=datos.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    if datos.email and usuario_repo.email_existe(db, email=datos.email):
        raise HTTPException(status_code=400, detail="El correo electrónico ya existe.")

    from app.security import hash_password
    usuario = Usuario(
        username=datos.username,
        nombre_completo=datos.nombre_completo,
        email=datos.email,
        password_hash=hash_password(datos.password),
        activo=True,
        debe_cambiar_password=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    escribir_auditoria(
        db, usuario=_, operacion="crear", entidad="usuario",
        registro_id=str(usuario.id),
        direccion_ip=request.client.host if request and request.client else None,
    )
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("usuarios.leer")),
):
    u = usuario_repo.get(db, usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return u


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: UUID,
    datos: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("usuarios.escribir")),
):
    usuario = usuario_repo.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    # Un usuario no puede elevar sus propios privilegios (manejo en roles).
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    escribir_auditoria(
        db, usuario=_, operacion="actualizar", entidad="usuario",
        registro_id=str(usuario.id),
        direccion_ip=request.client.host if request and request.client else None,
    )
    return usuario


@router.patch("/{usuario_id}/desactivar")
def desactivar_usuario(
    usuario_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("usuarios.escribir")),
):
    """Desactivar cuenta sin borrar su historial."""
    usuario = usuario_repo.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    usuario.activo = False
    db.add(usuario)
    db.commit()

    escribir_auditoria(
        db, usuario=_, operacion="desactivar", entidad="usuario",
        registro_id=str(usuario.id),
        motivo="Desactivación de cuenta",
        direccion_ip=request.client.host if request and request.client else None,
    )
    return {"mensaje": "Cuenta desactivada. El historial se conserva."}
