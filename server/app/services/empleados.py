"""Servicio de empleados: CRUD, historial de cambios, detección de duplicados."""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.employees import Empleado, ConfiguracionSalarial
from app.models.catalogs import Departamento, Puesto, Horario, AsignacionHorario
from app.models.security import Usuario, Auditoria
from app.repositories import empleado_repo, departamento_repo, puesto_repo, horario_repo, asignacion_horario_repo, configuracion_salarial_repo
from app.services.auth import escribir_auditoria


def validar_empleado_data(db: Session, *, numero_empleado: str, departamento_id, puesto_id=None, excluir_id=None) -> Optional[str]:
    """Valida reglas de negocio del empleado. Devuelve mensaje de error o None."""
    if departamento_repo.get(db, departamento_id) is None:
        return "El departamento especificado no existe."
    if not departamento_repo.get(db, departamento_id).activo:
        return "El departamento no está activo."
    if puesto_id is not None:
        puesto = puesto_repo.get(db, puesto_id)
        if puesto is None:
            return "El puesto especificado no existe."
        if not puesto.activo:
            return "El puesto no está activo."
        if str(puesto.departamento_id) != str(departamento_id):
            return "El puesto no pertenece al departamento seleccionado."
    # Detectar número de empleado duplicado
    existente = db.query(Empleado).filter(Empleado.numero_empleado == numero_empleado)
    if excluir_id:
        existente = existente.filter(Empleado.id != excluir_id)
    if existente.first():
        return f"Ya existe un empleado con el número {numero_empleado}."
    return None


def crear_empleado(db: Session, *, datos: dict, usuario: Usuario) -> Empleado:
    error = validar_empleado_data(
        db,
        numero_empleado=datos["numero_empleado"],
        departamento_id=datos["departamento_id"],
        puesto_id=datos.get("puesto_id"),
    )
    if error:
        raise ValueError(error)

    fecha_ingreso = datos["fecha_ingreso"]
    if isinstance(fecha_ingreso, str):
        fecha_ingreso = date.fromisoformat(fecha_ingreso)

    empleado = Empleado(
        numero_empleado=datos["numero_empleado"],
        nombre=datos["nombre"],
        apellido_paterno=datos["apellido_paterno"],
        apellido_materno=datos.get("apellido_materno"),
        departamento_id=datos["departamento_id"],
        puesto_id=datos.get("puesto_id"),
        fecha_ingreso=fecha_ingreso,
        estado=datos.get("estado", "activo"),
        usuario_creacion_id=usuario.id,
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="empleado",
        registro_id=str(empleado.id),
        valor_nuevo=f"{empleado.numero_empleado} - {empleado.nombre} {empleado.apellido_paterno}",
        motivo="Alta de empleado",
        direccion_ip=None,
    )
    return empleado


def actualizar_empleado(db: Session, *, empleado_id, datos: dict, usuario: Usuario) -> Empleado:
    empleado = empleado_repo.get(db, empleado_id)
    if not empleado:
        raise ValueError("Empleado no encontrado.")

    error = validar_empleado_data(
        db,
        numero_empleado=datos.get("numero_empleado", empleado.numero_empleado),
        departamento_id=datos.get("departamento_id", str(empleo.departamento_id)) if False else datos.get("departamento_id", empleado.departamento_id),
        puesto_id=datos.get("puesto_id", empleado.puesto_id),
        excluir_id=empleado.id,
    )
    if error:
        raise ValueError(error)

    valor_anterior = {
        "numero_empleado": empleado.numero_empleado,
        "nombre": empleado.nombre,
        "departamento_id": str(empleado.departamento_id),
        "estado": empleado.estado,
    }

    for campo in ["numero_empleado", "nombre", "apellido_paterno", "apellido_materno", "estado"]:
        if campo in datos:
            setattr(empleado, campo, datos[campo])
    if "departamento_id" in datos:
        empleado.departamento_id = datos["departamento_id"]
    if "puesto_id" in datos:
        empleado.puesto_id = datos["puesto_id"]
    if "fecha_ingreso" in datos:
        f = datos["fecha_ingreso"]
        empleado.fecha_ingreso = date.fromisoformat(f) if isinstance(f, str) else f
    empleado.usuario_modificacion_id = usuario.id

    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    escribir_auditoria(
        db, usuario=usuario, operacion="actualizar", entidad="empleado",
        registro_id=str(empleado.id),
        valor_anterior=str(valor_anterior),
        valor_nuevo=str({
            "numero_empleado": empleado.numero_empleado,
            "nombre": empleado.nombre,
            "departamento_id": str(empleado.departamento_id),
            "estado": empleado.estado,
        }),
        motivo="Actualización de datos de empleado",
    )
    return empleado


def cambiar_estado_empleado(db: Session, *, empleado_id, estado: str, usuario: Usuario) -> Empleado:
    """Dar de alta o baja administrativa con historial."""
    empleado = empleado_repo.get(db, empleado_id)
    if not empleado:
        raise ValueError("Empleado no encontrado.")
    estados_validos = ["activo", "baja_voluntaria", "baja_involuntaria", "licencia", "suspendido"]
    if estado not in estados_validos:
        raise ValueError(f"Estado no válido. Valores permitidos: {', '.join(estados_validos)}")

    anterior = empleado.estado
    empleado.estado = estado
    empleado.usuario_modificacion_id = usuario.id
    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    escribir_auditoria(
        db, usuario=usuario, operacion="cambiar_estado", entidad="empleado",
        registro_id=str(empleado.id),
        valor_anterior=anterior,
        valor_nuevo=estado,
        motivo=f"Cambio de estado de {anterior} a {estado}",
    )
    return empleado
