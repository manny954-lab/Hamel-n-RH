"""Endpoints de autenticación y seguridad.

- POST /api/v1/auth/login : inicio de sesión (usuario/contraseña).
- POST /api/v1/auth/first-admin : creación segura del primer administrador (solo si no hay usuarios).
- GET  /api/v1/auth/me : perfil del usuario autenticado.
- POST /api/v1/auth/logout : cierre de sesión (revoca token).
- POST /api/v1/auth/change-password : cambio de contraseña del usuario autenticado.
- POST /api/v1/auth/reset-password : restablecimiento de contraseña por administrador.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso, oauth2_scheme
from app.models.security import Usuario, Rol, Permiso, Sesion, usuario_rol, rol_permiso
from app.repositories.usuarios import usuario_repo
from app.repositories import rol_repo, permiso_repo
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
from app.services.auth import (
    autenticar_usuario,
    registrar_intento_fallido,
    resetear_intentos_fallidos,
    crear_sesion,
    revocar_sesion,
    escribir_auditoria,
)
from app.schemas import (
    LoginRequest, Token, UsuarioCreate, UsuarioOut, CambioPassword,
    RestablecerPassword,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


def _crear_roles_y_permisos_iniciales(db: Session):
    """Crea roles y permisos base si no existen."""
    permisos_base = [
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
    for clave, modulo, desc in permisos_base:
        if not db.query(Permiso).filter(Permiso.clave == clave).first():
            db.add(Permiso(clave=clave, descripcion=desc, modulo=modulo))
    db.commit()

    roles_base = {
        "Administrador del sistema": [
            "usuarios.leer", "usuarios.escribir", "empleados.leer", "empleados.escribir",
        "horarios.leer", "horarios.escribir", "asistencia.registrar", "asistencia.ajustar",
            "incidencias.leer", "incidencias.gestionar", "justificantes.leer",
            "justificantes.aprobar", "nomina.leer", "nomina.calcular", "nomina.cerrar",
            "reportes.leer", "auditoria.leer", "configuracion.escribir", "consulta_bd.ejecutar",
            "usuarios.eliminar", "empleados.eliminar",
        ],
        "Dirección o gerente": [
            "usuarios.leer", "empleados.leer", "horarios.leer", "asistencia.leer" if False else "asistencia.registrar",
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
            "empleados.leer", "asistencia.leer" if False else "asistencia.registrar",
            "incidencias.leer", "justificantes.leer", "reportes.leer",
        ],
        "Operador de asistencia": [
            "empleados.leer", "asistencia.registrar",
        ],
        "Auditor de solo lectura": [
            "usuarios.leer", "empleados.leer", "horarios.leer", "asistencia.leer" if False else "asistencia.registrar",
            "incidencias.leer", "justificantes.leer", "nomina.leer", "reportes.leer", "auditoria.leer",
        ],
    }
    for nombre, claves in roles_base.items():
        rol = db.query(Rol).filter(Rol.nombre == nombre).first()
        if not rol:
            rol = Rol(nombre=nombre, descripcion=f"Rol {nombre}")
            db.add(rol)
            db.commit()
            db.refresh(rol)
        for clave in claves:
            permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
            if permiso:
                ya = db.execute(
                    select(rol_permiso).where(
                        rol_permiso.c.rol_id == rol.id,
                        rol_permiso.c.permiso_id == permiso.id,
                    )
                ).first()
                if not ya:
                    db.execute(
                        rol_permiso.insert().values(rol_id=rol.id, permiso_id=permiso.id)
                    )
    db.commit()


@router.post("/first-admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_primer_administrador(
    datos: UsuarioCreate, db: Session = Depends(get_db), request: Request = None
):
    """Crea el primer administrador del sistema.

    Solo puede ejecutarse si no existe ningún usuario en la base de datos.
    Obliga a establecer credenciales propias; no hay cuenta administrativa universal.
    """
    if db.query(Usuario).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El primer administrador ya fue creado. Use el flujo de recuperación de contraseña.",
        )

    _crear_roles_y_permisos_iniciales(db)

    if usuario_repo.username_existe(db, username=datos.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe.",
        )

    admin_rol = db.query(Rol).filter(Rol.nombre == "Administrador del sistema").first()
    if not admin_rol:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo inicializar el rol de administrador.",
        )

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

    # Asignar rol de administrador
    from app.models.security import usuario_rol
    db.execute(
        usuario_rol.insert().values(usuario_id=usuario.id, rol_id=admin_rol.id)
    )
    db.commit()

    escribir_auditoria(
        db, usuario=usuario, operacion="crear", entidad="usuario",
        registro_id=str(usuario.id),
        valor_nuevo="primer administrador del sistema",
        motivo="Creación segura del primer administrador",
        direccion_ip=request.client.host if request and request.client else None,
    )
    return {"mensaje": "Primer administrador creado correctamente", "usuario_id": str(usuario.id)}


@router.post("/login", response_model=Token)
def login(
    datos: LoginRequest, db: Session = Depends(get_db), request: Request = None
):
    """Inicio de sesión con usuario y contraseña."""
    direccion_ip = request.client.host if request and request.client else None

    # Verificar bloqueo previo
    usuario = usuario_repo.get_por_username(db, username=datos.username)
    if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.now(timezone.utc):
        escribir_auditoria(
            db, usuario=usuario, operacion="login", entidad="usuario",
            registro_id=str(usuario.id), resultado="error",
            motivo="Intento de inicio de sesión en cuenta bloqueada",
            direccion_ip=direccion_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cuenta bloqueada temporalmente hasta {usuario.bloqueado_hasta}.",
        )

    usuario_autenticado = autenticar_usuario(db, datos.username, datos.password)
    if not usuario_autenticado:
        if usuario:
            registrar_intento_fallido(db, datos.username)
        escribir_auditoria(
            db, usuario=usuario, operacion="login", entidad="usuario",
            registro_id=str(usuario.id) if usuario else None,
            resultado="error",
            motivo="Credenciales inválidas",
            direccion_ip=direccion_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    resetear_intentos_fallidos(db, usuario_autenticado)
    usuario_autenticado.ultimo_acceso = datetime.now(timezone.utc)
    db.add(usuario_autenticado)
    db.commit()

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        data={"sub": usuario_autenticado.username, "uid": str(usuario_autenticado.id)},
        expires_delta=expires,
    )
    expiracion = datetime.now(timezone.utc) + expires

    # Decodificar JTI para guardar sesión
    payload = decode_token(token)
    crear_sesion(
        db, usuario=usuario_autenticado, token_jti=payload.get("jti", str(usuario_autenticado.id)),
        expiracion=expiracion, direccion_ip=direccion_ip,
        agente_usuario=request.headers.get("user-agent") if request else None,
    )

    escribir_auditoria(
        db, usuario=usuario_autenticado, operacion="login", entidad="usuario",
        registro_id=str(usuario_autenticado.id),
        motivo="Inicio de sesión exitoso",
        direccion_ip=direccion_ip,
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    """Perfil del usuario autenticado."""
    return usuario


@router.post("/logout")
def logout(
    usuario: Usuario = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Cierre de sesión: revoca el token actual."""
    payload = decode_token(token)
    if payload:
        jti = payload.get("jti")
        if jti:
            revocar_sesion(db, jti)
    escribir_auditoria(
        db, usuario=usuario, operacion="logout", entidad="usuario",
        registro_id=str(usuario.id),
        motivo="Cierre de sesión",
    )
    return {"mensaje": "Sesión cerrada"}


@router.post("/change-password")
def cambiar_password(
    datos: CambioPassword,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cambio de contraseña del usuario autenticado."""
    if not verify_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta.",
        )
    usuario.password_hash = hash_password(datos.password_nueva)
    usuario.debe_cambiar_password = False
    db.add(usuario)
    db.commit()
    escribir_auditoria(
        db, usuario=usuario, operacion="cambiar_password", entidad="usuario",
        registro_id=str(usuario.id),
        motivo="Cambio de contraseña por el usuario",
    )
    return {"mensaje": "Contraseña actualizada correctamente"}


@router.post("/reset-password")
def restablecer_password(
    datos: RestablecerPassword,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(requerir_permiso("usuarios.escribir")),
    username: Optional[str] = None,
):
    """Restablecimiento de contraseña por un administrador autorizado."""
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere el nombre de usuario a restablecer.",
        )
    objetivo = usuario_repo.get_por_username(db, username=username)
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    if not objetivo.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede restablecer la contraseña de una cuenta desactivada.",
        )
    objetivo.password_hash = hash_password(datos.password_nueva)
    objetivo.debe_cambiar_password = True
    objetivo.intentos_fallidos = 0
    objetivo.bloqueado_hasta = None
    db.add(objetivo)
    db.commit()
    escribir_auditoria(
        db, usuario=administrador, operacion="resetear_password", entidad="usuario",
        registro_id=str(objetivo.id),
        motivo="Restablecimiento de contraseña por administrador",
    )
    return {"mensaje": f"Contraseña restablecida para {username}"}
