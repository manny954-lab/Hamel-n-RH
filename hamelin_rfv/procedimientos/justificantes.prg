*==============================================================================
*  JUSTIFICANTES.PRG - Flujo de justificantes (solicitud, aprobación)
*==============================================================================

*------------------------------------------------------------------------------
* PROC GESTION_JUSTIFICANTES - Menú de justificantes
*------------------------------------------------------------------------------
PROCEDURE GESTION_JUSTIFICANTES
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== JUSTIFICANTES ==="
        @ 4, 10 SAY "1. Crear justificante"
        @ 5, 10 SAY "2. Listar justificantes pendientes"
        @ 6, 10 SAY "3. Aprobar/rechazar justificante"
        @ 7, 10 SAY "4. Listar todos"
        @ 8, 10 SAY "0. Volver"
        @ 10, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            DO CREAR_JUSTIFICANTE
        CASE nOpc = 2
            DO LISTAR_PENDIENTES
        CASE nOpc = 3
            DO DECIDIR_JUSTIFICANTE
        CASE nOpc = 4
            SELECT justificantes
            BROWSE NORMAL NOWAIT
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
* PROC CREAR_JUSTIFICANTE
*------------------------------------------------------------------------------
PROCEDURE CREAR_JUSTIFICANTE
    LOCAL nEmpId, cTipo, dFecha, cDesc
    nEmpId = VAL(INPUTBOX("ID de empleado:", "Crear justificante"))
    IF nEmpId = 0
        RETURN
    ENDIF

    cTipo = INPUTBOX("Tipo (medical, personal, etc.):", "Crear justificante")
    dFecha = DATE()
    cDesc = INPUTBOX("Descripción:", "Crear justificante")

    INSERT INTO justificantes (empleado_id, tipo, fecha_incidencia, descripcion, ;
                               estado, fecha_solicitud, fecha_creacion) VALUES ;
        (nEmpId, cTipo, dFecha, cDesc, "pendiente", DATETIME(), DATETIME())

    ESCRIBIR_AUDITORIA("crear", "justificante", ALLTRIM(STR(RECCOUNT())), .T., ;
        "Justificante creado: " + cTipo, "exito", g_cIpEstacion)
    MESSAGEBOX("Justificante creado (pendiente).", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC LISTAR_PENDIENTES - Muestra justificantes pendientes
*------------------------------------------------------------------------------
PROCEDURE LISTAR_PENDIENTES
    SELECT justificantes
    LOCATE FOR estado = "pendiente"
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC DECIDIR_JUSTIFICANTE - Aprueba o rechaza un justificante
*------------------------------------------------------------------------------
PROCEDURE DECIDIR_JUSTIFICANTE
    LOCAL nJustId, cEstado, cMotivo
    nJustId = VAL(INPUTBOX("ID de justificante:", "Decidir justificante"))
    IF nJustId = 0
        RETURN
    ENDIF

    SELECT justificantes
    LOCATE FOR id = nJustId
    IF !FOUND()
        MESSAGEBOX("Justificante no encontrado.", 16, "Error")
        RETURN
    ENDIF

    cEstado = INPUTBOX("Estado (aprobada/rechazada):", "Decidir justificante")
    IF UPPER(cEstado) <> "APROBADA" .AND. UPPER(cEstado) <> "RECHAZADA"
        MESSAGEBOX("Estado inválido.", 16, "Error")
        RETURN
    ENDIF

    cMotivo = ""
    IF UPPER(cEstado) = "RECHAZADA"
        cMotivo = INPUTBOX("Motivo del rechazo:", "Decidir justificante")
    ENDIF

    REPLACE justificantes.estado WITH cEstado, ;
        justificantes.fecha_decision WITH DATETIME(), ;
        justificantes.usuario_decision_id WITH VAL(g_cUsuarioId), ;
        justificantes.motivo_rechazo WITH cMotivo

    * Si se aprueba, marcar incidencias relacionadas como justificadas
    IF UPPER(cEstado) = "APROBADA"
        SELECT incidencias
        LOCATE FOR empleado_id = justificantes.empleado_id ;
            AND fecha = justificantes.fecha_incidencia ;
            AND justificada = .F.
        REPLACE incidencias.justificada WITH .T., ;
            incidencias.estado WITH "aprobada", ;
            incidencias.fecha_modificacion WITH DATETIME()
    ENDIF

    ESCRIBIR_AUDITORIA("decidir", "justificante", ALLTRIM(STR(nJustId)), .T., ;
        "Estado cambiado a " + cEstado, "exito", g_cIpEstacion)
    MESSAGEBOX("Justificante " + cEstado + ".", 64, "OK")
RETURN

RETURN