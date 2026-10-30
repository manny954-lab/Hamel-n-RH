*==============================================================================
*  UTIL.PRG - Utilitarios del sistema Hamelín RH (VFP 9.0)
*==============================================================================

*------------------------------------------------------------------------------
* FN_OBTENER_CONFIG - Lee un valor de configuración por clave
*------------------------------------------------------------------------------
FUNCTION FN_OBTENER_CONFIG(cClave)
    LOCAL cValor, nArea
    cValor = ""
    SELECT configuracion
    LOCATE FOR UPPER(clave) = UPPER(cClave)
    IF FOUND()
        cValor = ALLTRIM(valor)
    ENDIF
    RETURN cValor
ENDFUNC

*------------------------------------------------------------------------------
* FN_GUARDAR_CONFIG - Guarda o actualiza una clave de configuración
*------------------------------------------------------------------------------
FUNCTION FN_GUARDAR_CONFIG(cClave, cValor, cDescripcion)
    LOCAL nId
    SELECT configuracion
    LOCATE FOR UPPER(clave) = UPPER(cClave)
    IF FOUND()
        REPLACE valor WITH cValor, descripcion WITH cDescripcion, fecha_modificacion WITH DATETIME()
        nId = id
    ELSE
        INSERT INTO configuracion (clave, valor, descripcion, fecha_creacion) VALUES ;
            (cClave, cValor, cDescripcion, DATETIME())
        nId = RECCOUNT()
    ENDIF
    RETURN nId
ENDFUNC

*------------------------------------------------------------------------------
* FN_FECHA_ES_LABORABLE - Determina si una fecha es laborable según calendario
*------------------------------------------------------------------------------
FUNCTION FN_FECHA_ES_LABORABLE(dFecha, nHorarioId)
    LOCAL cDias, cNomDia, lEsLab, cFestivo
    LOCAL nDiaSem, aDias[1], nI

    * Obtener días laborables del horario
    SELECT horarios
    LOCATE FOR id = nHorarioId
    IF !FOUND()
        RETURN .F.
    ENDIF

    cDias = ALLTRIM(horarios.dias_laborables)
    IF EMPTY(cDias)
        cDias = "lunes,martes,miercoles,jueves,viernes,sabado"
    ENDIF

    * Día de la semana: 0=domingo en VFP (DAY(dFecha) devuelve 1..31, usar CDOW)
    cNomDia = LOWER(CDOW(dFecha))  && lunes, martes, etc. en español según configuración
    * CDOW depende del idioma; convertir a número estándar
    nDiaSem = VAL(SUBSTR(DTOC(dFecha), 1, 2))  && placeholder
    * En VFP español: DOW(dFecha) devuelve 1=domingo..7=sabado
    nDiaSem = DOW(dFecha)

    aDias = SPLIT(cDias, ",")
    lEsLab = .F.
    FOR nI = 1 TO ALEN(aDias, 1)
        IF LOWER(ALLTRIM(aDias[nI])) = "lunes" .AND. nDiaSem = 2
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "martes" .AND. nDiaSem = 3
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "miercoles" .AND. nDiaSem = 4
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "jueves" .AND. nDiaSem = 5
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "viernes" .AND. nDiaSem = 6
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "sabado" .AND. nDiaSem = 7
            lEsLab = .T.
        ELSEIF LOWER(ALLTRIM(aDias[nI])) = "domingo" .AND. nDiaSem = 1
            lEsLab = .T.
        ENDIF
    ENDFOR

    IF !lEsLab
        RETURN .F.
    ENDIF

    * Verificar festivos
    SELECT dias_festivos
    LOCATE FOR fecha = dFecha
    IF FOUND()
        RETURN .F.
    ENDIF

    RETURN .T.
ENDFUNC

*------------------------------------------------------------------------------
* FN_HASH_PASSWORD - Hash simulado de contraseña (VFP no tiene bcrypt nativo)
* En producción usar una DLL externa o función criptográfica real.
*------------------------------------------------------------------------------
FUNCTION FN_HASH_PASSWORD(cPassword)
    LOCAL cHash
    cHash = SYS(2015, cPassword + "HamelínRH2026")  && pseudo-hash basado en GUID + sal
    RETURN cHash
ENDFUNC

*------------------------------------------------------------------------------
* FN_VERIFICAR_PASSWORD - Compara contraseña contra hash almacenado
*------------------------------------------------------------------------------
FUNCTION FN_VERIFICAR_PASSWORD(cPassword, cHashGuardado)
    LOCAL cHashNuevo
    cHashNuevo = FN_HASH_PASSWORD(cPassword)
    RETURN (cHashNuevo = cHashGuardado)
ENDFUNC

*------------------------------------------------------------------------------
* FN_GENERAR_ID - Genera un identificador único alfanumérico (simula UUID corto)
*------------------------------------------------------------------------------
FUNCTION FN_GENERAR_ID()
    RETURN ALLTRIM(STR(RECCOUNT())) + SYS(2015)
ENDFUNC

*------------------------------------------------------------------------------
* FN_FECHA_UTC - Devuelve fecha y hora actual del sistema
*------------------------------------------------------------------------------
FUNCTION FN_FECHA_UTC()
    RETURN DATETIME()
ENDFUNC

*------------------------------------------------------------------------------
* FN_MINUTOS_ENTRE - Calcula minutos entre dos fechas/horas
*------------------------------------------------------------------------------
FUNCTION FN_MINUTOS_ENTRE(dInicio, dFin)
    RETURN INT((dFin - dInicio) * 24 * 60)
ENDFUNC

*------------------------------------------------------------------------------
* FN_NOMBRE_COMPLETO_EMPLEADO - Arma nombre completo de un empleado
*------------------------------------------------------------------------------
FUNCTION FN_NOMBRE_COMPLETO_EMPLEADO(nEmpleadoId)
    LOCAL cNom
    SELECT empleados
    LOCATE FOR id = nEmpleadoId
    IF FOUND()
        cNom = ALLTRIM(empleados.nombre) + " " + ALLTRIM(empleados.apellido_paterno)
        IF !EMPTY(empleados.apellido_materno)
            cNom = cNom + " " + ALLTRIM(empleados.apellido_materno)
        ENDIF
    ELSE
        cNom = ""
    ENDIF
    RETURN cNom
ENDFUNC

*------------------------------------------------------------------------------
* FN_USUARIO_TIENE_PERMISO - Verifica si el usuario logueado tiene un permiso
*------------------------------------------------------------------------------
FUNCTION FN_USUARIO_TIENE_PERMISO(cClavePermiso)
    LOCAL lTiene, nUsuarioId, nRolId, nPermisoId
    lTiene = .F.

    IF EMPTY(g_cUsuarioId)
        RETURN .F.
    ENDIF

    nUsuarioId = VAL(g_cUsuarioId)

    * Si es administrador, tiene todo
    IF g_lAdmin
        RETURN .T.
    ENDIF

    * Buscar permiso
    SELECT permisos
    LOCATE FOR UPPER(clave) = UPPER(cClavePermiso)
    IF !FOUND()
        RETURN .F.
    ENDIF
    nPermisoId = permisos.id

    * Buscar rol del usuario
    SELECT usuario_rol
    LOCATE FOR usuario_id = nUsuarioId
    IF !FOUND()
        RETURN .F.
    ENDIF
    nRolId = usuario_rol.rol_id

    * Verificar rol_permiso
    SELECT rol_permiso
    LOCATE FOR rol_id = nRolId .AND. permiso_id = nPermisoId
    IF FOUND()
        lTiene = .T.
    ENDIF

    RETURN lTiene
ENDFUNC

RETURN