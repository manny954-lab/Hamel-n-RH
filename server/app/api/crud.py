"""Router genérico de CRUD para catálogos simples."""

from typing import Type, TypeVar, List, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.repositories.base import BaseRepository
from app.services.auth import escribir_auditoria

ModelT = TypeVar("ModelT")
CreateT = TypeVar("CreateT", bound=BaseModel)
OutT = TypeVar("OutT", bound=BaseModel)


def crud_router(
    *,
    prefix: str,
    tags: List[str],
    model: Type[ModelT],
    repo: BaseRepository,
    create_schema: Type[CreateT],
    update_schema: Type[CreateT],
    out_schema: Type[OutT],
    permiso_leer: str,
    permiso_escribir: str,
    entidad: str,
    id_label: str = "id",
):
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=List[out_schema])
    def listar(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _: object = Depends(requerir_permiso(permiso_leer)),
    ):
        return repo.get_multi(db, skip=skip, limit=limit)

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    def crear(
        datos: create_schema,
        request: Request,
        db: Session = Depends(get_db),
        _: object = Depends(requerir_permiso(permiso_escribir)),
    ):
        obj = repo.create(db, obj_in=datos)
        escribir_auditoria(
            db, usuario=_, operacion="crear", entidad=entidad,
            registro_id=str(getattr(obj, id_label)),
            direccion_ip=request.client.host if request and request.client else None,
        )
        return obj

    @router.get("/{item_id}", response_model=out_schema)
    def obtener(
        item_id: UUID,
        db: Session = Depends(get_db),
        _: object = Depends(requerir_permiso(permiso_leer)),
    ):
        obj = repo.get(db, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{entidad} no encontrada.")
        return obj

    @router.patch("/{item_id}", response_model=out_schema)
    def actualizar(
        item_id: UUID,
        datos: update_schema,
        request: Request,
        db: Session = Depends(get_db),
        _: object = Depends(requerir_permiso(permiso_escribir)),
    ):
        obj = repo.get(db, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{entidad} no encontrada.")
        obj = repo.update(db, db_obj=obj, obj_in=datos)
        escribir_auditoria(
            db, usuario=_, operacion="actualizar", entidad=entidad,
            registro_id=str(getattr(obj, id_label)),
            direccion_ip=request.client.host if request and request.client else None,
        )
        return obj

    @router.delete("/{item_id}")
    def eliminar(
        item_id: UUID,
        request: Request,
        db: Session = Depends(get_db),
        _: object = Depends(requerir_permiso(permiso_escribir)),
    ):
        obj = repo.get(db, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{entidad} no encontrada.")
        repo.remove(db, id=item_id)
        escribir_auditoria(
            db, usuario=_, operacion="eliminar", entidad=entidad,
            registro_id=str(item_id),
            direccion_ip=request.client.host if request and request.client else None,
        )
        return {"mensaje": f"{entidad} eliminada"}

    return router
