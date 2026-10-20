"""Servicio de justificantes: estados, aprobación, historial de decisiones."""

from datetime import datetime, timezone, date
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.incidents import Justificante, Incidencia, ArchivoAdjunto
from app.models.employees import Empleado
from app.models.security import Usuario
from app.repositories import justificante_repo, incidencia_repo, archivo_adjunto_repo
from app.services.auth import escribir_auditoria


ESTADOS_VALIDOS = ["pendiente", "en_revision", "aprobada", "rechazada", "cancelada"]


def crear_justificante(
    db: Session,
    *,
    empleado_id,
    tipo: str,
    fecha_incidencia,
    descripcion: Optional[str] = None,
    documento_adjunto_id=None,
    usuario: Optional[Usuario] = None,
) -> Justificante:
    if isinstance(fecha_incidencia, str):
        fecha_incidencia = date.fromisoformat(fecha_incidencia)

    justificante = Justificante(
        empleado_id=empleado_id,
        tipo=tipo,
        fecha_incidencia=fecha_incidencia,
        descripcion=descripcion,
        estado="pendiente",
        fecha_solicitud=datetime.now(timezone.utc),
        documento_adjunto_id=documento_adjunto_id,
    )
    db.add(justificante)
    db.commit()
    db.refresh(justificante)

    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="justificante",
        registro_id=str(justificante.id),
        valor_nuevo=f"{tipo} {fecha_incidencia} estado=pendiente",
        motivo="Solicitud de justificante",
    )
    return justificante


def decidir_justificante(
    db: Session,
    *,
    justificante_id,
    estado: str,
    motivo: Optional[str],
    usuario: Usuario,
) -> Justificante:
    """Aprueba o rechaza un justificante. Solo usuarios autorizados."""
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado no válido: {estado}")

    justificante = justificante_repo.get(db, justificante_id)
    if not justificante:
        raise ValueError("Justificante no encontrado.")

    anterior = justificante.estado
    justificante.estado = estado
    justificante.fecha_decision = datetime.now(timezone.utc)
    justificante.usuario_decision_id = usuario.id
    if motivo and estado == "rechazada":
        justificante.motivo_rechazo = motivo
    db.add(justificante)
    db.commit()
    db.refresh(justificante)

    # Si se aprueba, marcar incidencias relacionadas como justificadas
    if estado == "aprobada":
        incidencias = (
            db.query(Incidencia)
            .filter(Incidencia.empleado_id == justificante.empleado_id)
            .filter(Incidencia.fecha == justificante.fecha_incidencia)
            .filter(Incidencia.justificada.is_(False))
            .all()
        )
        for inc in incidencias:
            inc.justificada = True
            inc.estado = "aprobada"
            db.add(inc)

    escribir_auditoria(
        db, usuario=usuario, operacion="decidir", entidad="justificante",
        registro_id=str(justificante.id),
        valor_anterior=anterior,
        valor_nuevo=estado,
        motivo=motivo or f"Cambio de estado a {estado}",
    )
    return justificante


def listar_justificantes_pendientes(db: Session) -> List[Justificante]:
    return (
        db.query(Justificante)
        .filter(Justificante.estado == "pendiente")
        .all()
    )
