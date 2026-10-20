"""Endpoints de auditoría (solo lectura)."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario, Auditoria
from app.schemas import AuditoriaOut

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoría"])


@router.get("", response_model=List[AuditoriaOut])
def listar_auditoria(
    entidad: Optional[str] = None,
    operacion: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("auditoria.leer")),
):
    from typing import Optional as _Optional
    q = db.query(Auditoria).order_by(Auditoria.fecha_hora.desc())
    if entidad:
        q = q.filter(Auditoria.entidad == entidad)
    if operacion:
        q = q.filter(Auditoria.operacion == operacion)
    return q.offset(skip).limit(limit).all()
