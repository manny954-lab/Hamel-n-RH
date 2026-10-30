*==============================================================================
*  SEGURIDAD.PRG - Autenticación, sesiones, roles, permisos y auditoría
*==============================================================================

*------------------------------------------------------------------------------
* FN_VALIDAR_USUARIO - Autentica usuario con control de intentos y bloqueo
*------------------------------------------------------------------------------
FUNCTION FN_VALIDAR_USUARIO(cUsuario, cPassword)
    LOCAL lOk, nIntentos, dBloqueo, nUserId, cHash
    LOCAL nMaxIntentos, nBloqueoMin
    LOCAL cValor

    lOk = .F.

    SELECT usuarios
    LOCATE FOR UPPER(username) = UPPER(cUsuario)
    IF !FOUND()
        RETURN .F.
    ENDIF

    nUserId   = usuarios.id
    cHash     = usuarios.password_hash
    nIntentos = usuarios.intentos_fallidos
    dBloqueo  = usuarios.bloqueado_hasta

    * Leer configuración de bloqueo
    cValor = FN_OBTENER_CONFIG("login_max_intentos", "5")
    nMaxIntentos = IIF(EMPTY(cValor), 5, VAL(cValor))
    cValor = FN_OBTENER_CONFIG("login_bloqueo_minutos", "15")
    nBloqueoMin = IIF(EMPTY(cValor), 15, VAL(cValor))

    * Verificar si está bloqueado
    IF dBloqueo > DATETIME()
        RETURN .F.  && cuenta bloqueada
    ENDIF

    * Verificar contraseña
    IF !FN_VERIFICAR_PASSWORD(cPassword, cHash)
        * Incrementar intentos fallidos
        REPLACE usuarios.intentos_fallidos WITH nIntentos + 1
        IF nIntentos + 1 >= nMaxIntentos
            dBloqueo = DATETIME() + (nBloqueoMin / 1440)
            REPLACE usuarios.bloqueado_hasta WITH dBloqueo
        ENDIF
        RETURN .F.
    ENDIF

    * Éxito: resetear intentos y actualizar último acceso
    REPLACE usuarios.intentos_fallidos WITH 0
    REPLACE usuarios.bloqueado_hasta WITH NULL
    REPLACE usuarios.ultimo_acceso WITH DATETIME()

    RETURN .T.
ENDFUNC

*------------------------------------------------------------------------------
* FN_OBTENER_DATOS_USUARIO - Devuelve ID, nombre y rol del usuario autenticado
*------------------------------------------------------------------------------
FUNCTION FN_OBTENER_DATOS_USUARIO(cUsuario)
    LOCAL nId, cNom, cRol
    nId = 0
    cNom = ""
    cRol = ""

    SELECT usuarios
    LOCATE FOR UPPER(username) = UPPER(cUsuario)
    IF FOUND()
        nId = usuarios.id
        cNom = usuarios.nombre_completo
    ENDIF

    * Obtener rol
    SELECT usuario_rol
    LOCATE FOR usuario_id = nId
    IF FOUND()
        SELECT roles
        LOCATE FOR id = usuario_rol.rol_id
        IF FOUND()
            cRol = roles.nombre
        ENDIF
    ENDIF

    RETURN nId, cNom, cRol
ENDFUNC

*------------------------------------------------------------------------------
* FN_CREAR_SESION - Registra una nueva sesión de usuario
*------------------------------------------------------------------------------
FUNCTION FN_CREAR_SESION(nUsuarioId, cIp)
    LOCAL nSesionId, cJti
    cJti = SYS(2015)

    INSERT INTO sesiones (usuario_id, token_jti, fecha_expiracion, ;
                          direccion_ip, fecha_creacion) VALUES ;
        (nUsuarioId, cJti, DATETIME() + (VAL(FN_OBTENER_CONFIG("access_token_expire_minutes","30"))/1440), ;
         cIp, DATETIME())

    nSesionId = RECCOUNT("sesiones")
    RETURN nSesionId
ENDFUNC

*------------------------------------------------------------------------------
* FN_REVOCAR_SESION - Marca una sesión como revocada
*------------------------------------------------------------------------------
FUNCTION FN_REVOCAR_SESION(nSesionId)
    SELECT sesiones
    LOCATE FOR id = nSesionId
    IF FOUND()
        REPLACE fecha_revocacion WITH DATETIME()
    ENDIF
RETURN

*------------------------------------------------------------------------------
* ESCRIBIR_AUDITORIA - Escribe un registro en la tabla auditoría
*------------------------------------------------------------------------------
PROCEDURE ESCRIBIR_AUDITORIA(cOperacion, cEntidad, cRegistroId, lExito, ;
                             cMotivo, cResultado, cIp)
    LOCAL nUsuarioId
    nUsuarioId = IIF(EMPTY(g_cUsuarioId), 0, VAL(g_cUsuarioId))

    INSERT INTO auditoria (usuario_id, fecha_hora, operacion, entidad, ;
                           registro_id, valor_anterior, valor_nuevo, ;
                           motivo, resultado, direccion_ip, detalles) VALUES ;
        (nUsuarioId, DATETIME(), cOperacion, cEntidad, cRegistroId, ;
         "", "", cMotivo, cResultado, cIp, "")
RETURN

*------------------------------------------------------------------------------
* FN_OBTENER_ROL_USUARIO - Devuelve el nombre del rol de un usuario
*------------------------------------------------------------------------------
FUNCTION FN_OBTENER_ROL_USUARIO(nUsuarioId)
    LOCAL cRol
    cRol = ""
    SELECT usuario_rol
    LOCATE FOR usuario_id = nUsuarioId
    IF FOUND()
        SELECT roles
        LOCATE FOR id = usuario_rol.rol_id
        IF FOUND()
            cRol = roles.nombre
        ENDIF
    ENDIF
    RETURN cRol
ENDFUNC

*------------------------------------------------------------------------------
* FN_BLOQUEAR_USUARIO - Bloquea temporalmente un usuario
*------------------------------------------------------------------------------
PROCEDURE FN_BLOQUEAR_USUARIO(nUsuarioId, nMinutos)
    LOCAL dHasta
    dHasta = DATETIME() + (nMinutos / 1440)
    SELECT usuarios
    LOCATE FOR id = nUsuarioId
    IF FOUND()
        REPLACE bloqueado_hasta WITH dHasta
    ENDIF
RETURN

*------------------------------------------------------------------------------
* FN_DESBLOQUEAR_USUARIO - Quita bloqueo de un usuario
*------------------------------------------------------------------------------
PROCEDURE FN_DESBLOQUEAR_USUARIO(nUsuarioId)
    SELECT usuarios
    LOCATE FOR id = nUsuarioId
    IF FOUND()
        REPLACE bloqueado_hasta WITH NULL, intentos_fallidos WITH 0
    ENDIF
RETURN

*------------------------------------------------------------------------------
* PROC MENU_USUARIOS - Mantenimiento de usuarios y roles (solo admin)
*------------------------------------------------------------------------------
PROCEDURE MENU_USUARIOS
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== USUARIOS Y PERMISOS ==="
        @ 4, 10 SAY "1. Listar usuarios"
        @ 5, 10 SAY "2. Crear usuario"
        @ 6, 10 SAY "3. Editar usuario"
        @ 7, 10 SAY "4. Asignar rol"
        @ 8, 10 SAY "5. Cambiar contraseña (admin)"
        @ 9, 10 SAY "6. Desbloquear cuenta"
        @ 10, 10 SAY "0. Volver"
        @ 12, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            DO LISTAR_USUARIOS
        CASE nOpc = 2
            DO CREAR_USUARIO
        CASE nOpc = 3
            DO EDITAR_USUARIO
        CASE nOpc = 4
            DO ASIGNAR_ROL
        CASE nOpc = 5
            DO CAMBIAR_PASSWORD_ADMIN
        CASE nOpc = 6
            DO DESBLOQUEAR_USUARIO_MENU
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE LISTAR_USUARIOS
    SELECT usuarios
    BROWSE NORMAL NOWAIT
RETURN

PROCEDURE CREAR_USUARIO
    LOCAL cUser, cPass, cNom, cEmail
    cUser = SPACE(100)
    cPass = SPACE(100)
    cNom  = SPACE(200)
    cEmail= SPACE(200)

    @ 1, 10 SAY "Nuevo usuario:" GET cUser
    @ 3, 10 SAY "Contraseña:" GET cPass PICTURE "!"
    @ 5, 10 SAY "Nombre completo:" GET cNom
    @ 7, 10 SAY "Email:" GET cEmail
    READ

    IF EMPTY(cUser) .OR. EMPTY(cPass) .OR. EMPTY(cNom)
        MESSAGEBOX("Usuario, contraseña y nombre son obligatorios.", 16, "Error")
        RETURN
    ENDIF

    SELECT usuarios
    LOCATE FOR UPPER(username) = UPPER(cUser)
    IF FOUND()
        MESSAGEBOX("El usuario ya existe.", 16, "Error")
        RETURN
    ENDIF

    INSERT INTO usuarios (username, nombre_completo, email, password_hash, ;
                          activo, intentos_fallidos, debe_cambiar_password, ;
                          fecha_creacion) VALUES ;
        (cUser, cNom, cEmail, FN_HASH_PASSWORD(cPass), .T., 0, .T., DATETIME())

    ESCRIBIR_AUDITORIA("crear", "usuario", ALLTRIM(STR(RECCOUNT())), .T., ;
        "Usuario creado", "exito", g_cIpEstacion)
    MESSAGEBOX("Usuario creado correctamente.", 64, "OK")
RETURN

PROCEDURE EDITAR_USUARIO
    LOCAL nId, cNom, cEmail, lActivo
    nId = VAL(INPUTBOX("ID de usuario a editar:", "Editar usuario"))
    IF nId = 0
        RETURN
    ENDIF

    SELECT usuarios
    LOCATE FOR id = nId
    IF !FOUND()
        MESSAGEBOX("Usuario no encontrado.", 16, "Error")
        RETURN
    ENDIF

    cNom = usuarios.nombre_completo
    cEmail = usuarios.email
    lActivo = usuarios.activo

    @ 1, 10 SAY "Nombre completo:" GET cNom
    @ 3, 10 SAY "Email:" GET cEmail
    @ 5, 10 SAY "Activo:" GET lActivo
    READ

    REPLACE nombre_completo WITH cNom, email WITH cEmail, activo WITH lActivo
    ESCRIBIR_AUDITORIA("editar", "usuario", ALLTRIM(STR(nId)), .T., "Datos actualizados", "exito")
    MESSAGEBOX("Usuario actualizado.", 64, "OK")
RETURN

PROCEDURE ASIGNAR_ROL
    LOCAL nUserId, nRolId
    nUserId = VAL(INPUTBOX("ID de usuario:", "Asignar rol"))
    nRolId  = VAL(INPUTBOX("ID de rol:", "Asignar rol"))

    SELECT usuario_rol
    LOCATE FOR usuario_id = nUserId
    IF FOUND()
        REPLACE rol_id WITH nRolId
    ELSE
        INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (nUserId, nRolId)
    ENDIF
    MESSAGEBOX("Rol asignado.", 64, "OK")
RETURN

PROCEDURE CAMBIAR_PASSWORD_ADMIN
    LOCAL nUserId, cPass
    nUserId = VAL(INPUTBOX("ID de usuario:", "Cambiar contraseña"))
    cPass   = INPUTBOX("Nueva contraseña:", "Cambiar contraseña", "", 2)

    SELECT usuarios
    LOCATE FOR id = nUserId
    IF FOUND()
        REPLACE password_hash WITH FN_HASH_PASSWORD(cPass), ;
                 debe_cambiar_password WITH .T., ;
                 intentos_fallidos WITH 0, ;
                 bloqueado_hasta WITH NULL
        MESSAGEBOX("Contraseña cambiada.", 64, "OK")
    ELSE
        MESSAGEBOX("Usuario no encontrado.", 16, "Error")
    ENDIF
RETURN

PROCEDURE DESBLOQUEAR_USUARIO_MENU
    LOCAL nUserId
    nUserId = VAL(INPUTBOX("ID de usuario a desbloquear:", "Desbloquear"))
    FN_DESBLOQUEAR_USUARIO(nUserId)
    MESSAGEBOX("Cuenta desbloqueada.", 64, "OK")
RETURN

RETURN