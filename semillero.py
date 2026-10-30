"""Semillero de datos de demostración para Hamelín RH.

Todo se escribe con SQLAlchemy sobre el mismo archivo SQLite local
(hamelin_rh.db) que usa el servidor. Es idempotente: se puede volver a ejecutar
sin duplicar datos. No requiere llamadas HTTP ni servidor PostgreSQL.

Puebla:
  - Roles y permisos base.
  - Usuarios de demo (admin, rrhh, operador, supervisor) con sus roles.
  - Departamentos y horarios.
  - Los 45 empleados (APELLIDOS + NOMBRES), cada uno con su horario y sueldo.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import date, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "server"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.database import Base, engine as engine_api
from app.core.config import settings
from app.models import (  # noqa: F401 (registra todos los modelos y sus relaciones)
    security, catalogs, employees, attendance, incidents, payroll,
)
from app.models.security import (
    Usuario, Rol, Permiso, usuario_rol, rol_permiso,
)
from app.models.catalogs import Departamento, Horario, AsignacionHorario as AH
from app.models.employees import Empleado, ConfiguracionSalarial
from app.security import hash_password
from app.services import demo

DB_PATH = "/home/Emmanuel/Documentos/OPENCODE/hamelin_rh.db"
ENGINE = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    future=True,
)

# --------------------------------------------------------------------------- datos

USUARIOS_DEMO = [
    {"username": "admin.coolcircle", "nombre_completo": "Administrador Sistema",
     "email": "admin@coolcircle.mx", "password": "AdminSeguro2026!",
     "rol": "Administrador del sistema"},
    {"username": "rrhh.coolcircle", "nombre_completo": "RRHH Cool Circle",
     "email": "rrhh@coolcircle.mx", "password": "RRHH2026!",
     "rol": "Recursos Humanos"},
    {"username": "operador.coolcircle", "nombre_completo": "Operador Asistencia",
     "email": "operador@coolcircle.mx", "password": "Operador2026!",
     "rol": "Operador de asistencia"},
    {"username": "supervisor.coolcircle", "nombre_completo": "Supervisor Departamento",
     "email": "supervisor@coolcircle.mx", "password": "Supervisor2026!",
     "rol": "Supervisor de departamento"},
]

PERMISOS_BASE = [
    ("usuarios.leer", "Usuarios", "Leer usuarios"),
    ("usuarios.escribir", "Usuarios", "Crear/editar usuarios"),
    ("usuarios.eliminar", "Usuarios", "Eliminar usuarios"),
    ("empleados.leer", "Empleados", "Leer empleados"),
    ("empleados.escribir", "Empleados", "Crear/editar empleados"),
    ("empleados.eliminar", "Empleados", "Eliminar empleados"),
    ("horarios.leer", "Horarios", "Leer horarios"),
    ("horarios.escribir", "Horarios", "Configurar horarios"),
    ("asistencia.registrar", "Asistencia", "Registrar eventos de asistencia"),
    ("asistencia.ajustar", "Asistencia", "Corregir eventos de asistencia"),
    ("incidencias.leer", "Incidencias", "Leer incidencias"),
    ("incidencias.gestionar", "Incidencias", "Gestionar incidencias"),
    ("justificantes.leer", "Justificantes", "Leer justificantes"),
    ("justificantes.aprobar", "Justificantes", "Aprobar/rechazar justificantes"),
    ("nomina.leer", "Nómina", "Leer prenómina"),
    ("nomina.calcular", "Nómina", "Calcular prenómina"),
    ("nomina.cerrar", "Nómina", "Cerrar periodos de nómina"),
    ("reportes.leer", "Reportes", "Generar reportes"),
    ("auditoria.leer", "Auditoría", "Leer auditoría"),
    ("configuracion.escribir", "Configuración", "Modificar configuración del sistema"),
    ("consulta_bd.ejecutar", "Consulta BD", "Ejecutar consultas de base de datos"),
]

ROLES_BASE = {
    "Administrador del sistema": [
        "usuarios.leer", "usuarios.escribir", "empleados.leer", "empleados.escribir",
        "horarios.leer", "horarios.escribir", "asistencia.registrar", "asistencia.ajustar",
        "incidencias.leer", "incidencias.gestionar", "justificantes.leer",
        "justificantes.aprobar", "nomina.leer", "nomina.calcular", "nomina.cerrar",
        "reportes.leer", "auditoria.leer", "configuracion.escribir", "consulta_bd.ejecutar",
        "usuarios.eliminar", "empleados.eliminar",
    ],
    "Dirección o gerente": [
        "usuarios.leer", "empleados.leer", "horarios.leer", "asistencia.registrar",
        "incidencias.leer", "justificantes.leer", "nomina.leer", "reportes.leer", "auditoria.leer",
    ],
    "Recursos Humanos": [
        "empleados.leer", "empleados.escribir", "asistencia.registrar", "incidencias.leer",
        "incidencias.gestionar", "justificantes.leer", "justificantes.aprobar",
        "nomina.leer", "reportes.leer", "auditoria.leer",
    ],
    "Responsable de nómina": [
        "empleados.leer", "incidencias.leer", "justificantes.leer",
        "nomina.leer", "nomina.calcular", "nomina.cerrar", "reportes.leer",
    ],
    "Supervisor de departamento": [
        "empleados.leer", "asistencia.registrar", "incidencias.leer", "justificantes.leer",
        "reportes.leer",
    ],
    "Operador de asistencia": [
        "empleados.leer", "asistencia.registrar",
    ],
    "Auditor de solo lectura": [
        "usuarios.leer", "empleados.leer", "horarios.leer", "asistencia.registrar",
        "incidencias.leer", "justificantes.leer", "nomina.leer", "reportes.leer", "auditoria.leer",
    ],
}

# (codigo, nombre, clave_horario, sueldo_base)
DEPARTAMENTOS = [
    ("ADM", "Administración", "ADM-08-16", 16000),
    ("VEN", "Ventas", "VEN-09-17", 12500),
    ("ALM", "Almacén", "ALM-07-15", 11000),
    ("REP", "Reparto", "REP-0630-1430", 10000),
    ("MAN", "Mantenimiento", "MAN-0830-1630", 12000),
]

# Empleados: "APELLIDOS NOMBRES" (apellidos primero, tal como se solicitó).
EMPLEADOS_APELLIDOS_NOMBRES = [
    "AGUILERA ROSALES JOSE ERNESTO",
    "AMADOR ROMO DERECK NAIM",
    "AVILA BAUTISTA DANIEL",
    "BARRERA MEZA CIELODERITH GENESIS",
    "BARRERA VALDEZ EMILIO",
    "BRAVO CASTILLO MIGUEL ORLANDO",
    "CAMPOS RAMIREZ KIMBERLY AND",
    "CARDENAS MONTOYA JORGE MANUEL",
    "CARDONA DE LIRA FRIDA VICTORIA",
    "CASTILLO MARTINEZ ANGEL FABIAN",
    "CONTRERAS MORALES JESUS",
    "DE LIRA SANTIAGO ALEXANDER",
    "DIAZ LOPEZ ZAID AZAEL",
    "DIAZ MAYAGOITIA IAN CARLO",
    "GALAVIZ QUIROZ EDGAR FRANCISCO",
    "GALLARDO SOLANO EVELYN JACQUELINE",
    "GARCIA MEDINA ANA SOFIA",
    "GONGORA RODRIGUEZ JORGE ARMANDO",
    "GUTIERREZ PAZ BILGAHI MIKEYLA",
    "GUZMAN MENDEZ ANGELICA NAOMI",
    "HERNANDEZ HERNANDEZ ERICK NICOLAS",
    "LOMELI GUTIERREZ GUSTAVO SANTIAGO",
    "LOREDO PARRA DIANA",
    "LUNA TAMAYO MILDRED SCARLETT",
    "MATA GONZALEZ DAFNE NAOMY",
    "MOLINA PEREZ MIA FATIMA",
    "MONTOYA LARRANAGA ISABELLA",
    "MOSQUEDA DIAZ VIOLETA SAYDI",
    "NAJERA BALLIN LEONARDO",
    "PACHECO VALENCIA CARLOS ADRIAN",
    "PALACIO MARIN MIGUEL",
    "PARRAS REYES ANDREA SCARLETT",
    "PEDROZA GAMEZ LIZBETH",
    "PONCE RODRIGUEZ KARIME IRAIS",
    "RAMIREZ DAVILA ALMA JOCABET",
    "REYES CUEVAS MATEO",
    "REYES HERNANDEZ ALEJANDRA SOFIA",
    "RODRIGUEZ ESPARZA HEINZE FRANLLELY",
    "SANCHEZ PEREZ YOSGART ALBERTO",
    "SANTOS CHAVEZ WILLIAM",
    "SAUCEDO BOCANEGRA ROXANA",
    "SOTO PEDROZA DILAN SANTIAGO",
    "TAPIA NAVARRO LUIS ANGEL",
    "TERAN ORTIZ CHRISTOPHER EMMANUEL",
    "TISCARENO MARENTES JESUS OMAR",
]

FECHAS_INGRESO = [
    "2022-03-15", "2023-01-10", "2023-02-01", "2023-03-10", "2023-01-15",
    "2022-07-20", "2023-04-01", "2023-05-10", "2023-06-01", "2023-07-01",
    "2023-08-01", "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01",
    "2024-01-15", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01",
    "2024-06-01", "2024-07-01", "2024-08-01", "2024-09-01", "2024-10-01",
    "2024-11-01", "2024-12-01", "2025-01-15", "2025-02-01", "2025-03-01",
    "2025-04-01", "2025-05-01", "2025-06-01", "2025-07-01", "2025-08-01",
    "2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01", "2026-01-01",
    "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01",
]


def parsear_nombre(apellidos_nombres: str):
    """APELLIDOS NOMBRES -> (apellido_paterno, apellido_materno, nombres)."""
    partes = apellidos_nombres.split()
    ap_paterno = partes[0] if partes else ""
    ap_materno = partes[1] if len(partes) > 1 else ""
    if len(partes) > 2:
        nombres = " ".join(partes[2:])
    elif len(partes) == 2:
        nombres = partes[1]
    else:
        nombres = partes[0] if partes else ""
    return ap_paterno, ap_materno, nombres


def crear_roles_y_permisos(db: Session):
    for clave, modulo, desc in PERMISOS_BASE:
        if not db.query(Permiso).filter(Permiso.clave == clave).first():
            db.add(Permiso(clave=clave, descripcion=desc, modulo=modulo))
    db.commit()
    for nombre, claves in ROLES_BASE.items():
        rol = db.query(Rol).filter(Rol.nombre == nombre).first()
        if not rol:
            rol = Rol(nombre=nombre, descripcion=f"Rol {nombre}")
            db.add(rol)
            db.commit()
            db.refresh(rol)
        for clave in claves:
            permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
            if not permiso:
                continue
            ya = db.execute(
                rol_permiso.select().where(
                    rol_permiso.c.rol_id == rol.id,
                    rol_permiso.c.permiso_id == permiso.id,
                )
            ).first()
            if not ya:
                db.execute(
                    rol_permiso.insert().values(rol_id=rol.id, permiso_id=permiso.id)
                )
    db.commit()
    print("Roles y permisos creados.")


def crear_usuarios(db: Session) -> dict[str, Usuario]:
    usuarios: dict[str, Usuario] = {}
    for u in USUARIOS_DEMO:
        existente = db.query(Usuario).filter(Usuario.username == u["username"]).first()
        if existente:
            usuarios[u["username"]] = existente
            continue
        usuario = Usuario(
            username=u["username"],
            nombre_completo=u["nombre_completo"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            activo=True,
            debe_cambiar_password=False,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        usuarios[u["username"]] = usuario
        print(f"Usuario creado: {u['username']}")
    return usuarios


def asignar_roles(db: Session, usuarios: dict[str, Usuario]):
    for u in USUARIOS_DEMO:
        usuario = usuarios[u["username"]]
        rol = db.query(Rol).filter(Rol.nombre == u["rol"]).first()
        if not rol:
            print(f"Rol no encontrado: {u['rol']}")
            continue
        ya = db.execute(
            usuario_rol.select().where(
                usuario_rol.c.usuario_id == usuario.id,
                usuario_rol.c.rol_id == rol.id,
            )
        ).first()
        if not ya:
            db.execute(
                usuario_rol.insert().values(usuario_id=usuario.id, rol_id=rol.id)
            )
    db.commit()
    print("Roles asignados a usuarios.")


def crear_departamentos_y_horarios(db: Session):
    dep_ids: dict[str, object] = {}
    horario_ids: dict[str, object] = {}
    for codigo, nombre, horario_cod, sueldo in DEPARTAMENTOS:
        dep = db.query(Departamento).filter(Departamento.codigo == codigo).first()
        if not dep:
            dep = Departamento(codigo=codigo, nombre=nombre)
            db.add(dep)
            db.commit()
            db.refresh(dep)
        dep_ids[codigo] = dep.id

        # horario_cod tiene formato "DEPTO-HHMM" o "DEPTO-HH-MM" (ej. ADM-08-16,
        # REP-0630-1430, MAN-0830-1630)
        def parse_hhmm(s: str) -> time:
            s = s.strip()
            if len(s) == 2:
                return time(int(s), 0)
            return time(int(s[:2]), int(s[2:]))

        partes = horario_cod.split("-")
        h_entrada = parse_hhmm(partes[1])
        h_salida = parse_hhmm(partes[2])
        hor = db.query(Horario).filter(Horario.codigo == horario_cod).first()
        if not hor:
            hor = Horario(
                codigo=horario_cod,
                nombre=f"{nombre} {horario_cod}",
                hora_entrada=h_entrada,
                hora_salida=h_salida,
                cruza_medianoche=False,
                periodo_comida_minutos=0,
                dias_laborables='["lunes","martes","miercoles","jueves","viernes","sabado"]',
                tolerancia_minutos=10,
            )
            db.add(hor)
            db.commit()
            db.refresh(hor)
        horario_ids[codigo] = hor.id
    print("Departamentos y horarios creados.")
    return dep_ids, horario_ids


def crear_empleados(db: Session, dep_ids, horario_ids, admin_id: str):
    for idx, nombre_completo in enumerate(EMPLEADOS_APELLIDOS_NOMBRES):
        numero = f"EMP-{idx + 1:03d}"
        depto_codigo = DEPARTAMENTOS[idx % len(DEPARTAMENTOS)][0]
        sueldo = DEPARTAMENTOS[idx % len(DEPARTAMENTOS)][3]
        fecha_ingreso = date.fromisoformat(FECHAS_INGRESO[idx % len(FECHAS_INGRESO)])

        ya = db.query(Empleado).filter(Empleado.numero_empleado == numero).first()
        if ya:
            continue

        ap_paterno, ap_materno, nombres = parsear_nombre(nombre_completo)
        empleado = Empleado(
            numero_empleado=numero,
            nombre=nombres,
            apellido_paterno=ap_paterno,
            apellido_materno=ap_materno or None,
            departamento_id=dep_ids[depto_codigo],
            fecha_ingreso=fecha_ingreso,
            estado="activo",
            usuario_creacion_id=admin_id,
        )
        db.add(empleado)
        db.commit()
        db.refresh(empleado)

        db.add(AH(
            empleado_id=empleado.id,
            horario_id=horario_ids[depto_codigo],
            fecha_inicio_vigencia=fecha_ingreso,
        ))

        db.add(ConfiguracionSalarial(
            id=uuid.uuid4(),
            empleado_id=empleado.id,
            sueldo_base=float(sueldo),
            periodicidad="mensual",
            fecha_vigencia=fecha_ingreso,
            usuario_alta_id=admin_id,
            motivo="Demo",
        ))
        db.commit()
    print(f"Empleados creados: {len(EMPLEADOS_APELLIDOS_NOMBRES)}")


def main() -> None:
    print("=== Hamelín RH - Semillero de demostración ===")
    print(f"Base de datos: {DB_PATH}")

    # 1. Estructura (idempotente)
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=ENGINE)
    print("Tablas verificadas/creadas.")

    # 2. Datos (un solo motor, escritura secuencial: sin bloqueos de SQLite)
    with Session(ENGINE) as db:
        crear_roles_y_permisos(db)
        usuarios = crear_usuarios(db)
        asignar_roles(db, usuarios)
        admin_id = usuarios["admin.coolcircle"].id  # objeto uuid.UUID
        dep_ids, horario_ids = crear_departamentos_y_horarios(db)
        crear_empleados(db, dep_ids, horario_ids, admin_id)

    # Generar asistencias simuladas para los últimos 5 días (demo lista para vender)
    demo.generar_asistencias_demo(db, dias_atras=5, usuario=None)
    # Generar faltas automáticas para ayer
    demo.generar_faltas_automaticas(db, usuario=None)

    # Notificar al servidor (si está corriendo) que recycle su pool para ver
    # los nuevos datos sin reiniciar.
    engine_api.dispose()

    print("\n==========================================")
    print("SEMILLADO COMPLETADO")
    print("==========================================")
    print("Credenciales de acceso:")
    for u in USUARIOS_DEMO:
        print(f"  {u['username']} / {u['password']}  ({u['rol']})")
    print(f"\nEmpleados: {len(EMPLEADOS_APELLIDOS_NOMBRES)} (EMP-001 a EMP-045)")
    print(f"Servidor API: http://127.0.0.1:8001")
    print("Cliente: ./dist/hamelin-rh  (o ./iniciar_hamelin_rh.sh)")


if __name__ == "__main__":
    main()
