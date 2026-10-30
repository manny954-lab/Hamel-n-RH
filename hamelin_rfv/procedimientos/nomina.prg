*==============================================================================
*  NOMINA.PRG - Periodos, cálculo de prenómina, ajustes y cierre
*==============================================================================

*------------------------------------------------------------------------------
* PROC GESTION_NOMINA - Menú de nómina
*------------------------------------------------------------------------------
PROCEDURE GESTION_NOMINA
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== PRENÓMINA ==="
        @ 4, 10 SAY "1. Crear periodo"
        @ 5, 10 SAY "2. Listar periodos"
        @ 6, 10 SAY "3. Calcular prenómina"
        @ 7, 10 SAY "4. Ver resultados"
        @ 8, 10 SAY "5. Proponer ajuste"
        @ 9, 10 SAY "6. Decidir propuesta"
        @ 10, 10 SAY "7. Cerrar periodo"
        @ 11, 10 SAY "0. Volver"
        @ 13, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            DO CREAR_PERIODO_NOMINA
        CASE nOpc = 2
            SELECT periodos_nomina
            BROWSE NORMAL NOWAIT
        CASE nOpc = 3
            DO CALCULAR_PRENOMINA_MENU
        CASE nOpc = 4
            DO VER_RESULTADOS_NOMINA
        CASE nOpc = 5
            DO PROPONER_AJUSTE
        CASE nOpc = 6
            DO DECIDIR_PROPUESTA
        CASE nOpc = 7
            DO CERRAR_PERIODO_MENU
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
* PROC CREAR_PERIODO_NOMINA
*------------------------------------------------------------------------------
PROCEDURE CREAR_PERIODO_NOMINA
    LOCAL cNom, dInicio, dFin
    cNom = SPACE(150)
    dInicio = DATE()
    dFin = DATE()

    @ 2, 10 SAY "Nombre del periodo:" GET cNom
    @ 4, 10 SAY "Fecha inicio:" GET dInicio
    @ 6, 10 SAY "Fecha fin:" GET dFin
    READ

    IF EMPTY(cNom)
        MESSAGEBOX("El nombre es obligatorio.", 16, "Error")
        RETURN
    ENDIF

    IF dFin < dInicio
        MESSAGEBOX("La fecha fin no puede ser anterior a la inicio.", 16, "Error")
        RETURN
    ENDIF

    * Validar solapamiento
    SELECT periodos_nomina
    LOCATE FOR fecha_inicio <= dFin .AND. fecha_fin >= dInicio
    IF FOUND()
        MESSAGEBOX("El periodo se solapa con otro existente.", 16, "Error")
        RETURN
    ENDIF

    INSERT INTO periodos_nomina (nombre, fecha_inicio, fecha_fin, estado, fecha_creacion) VALUES ;
        (cNom, dInicio, dFin, "abierto", DATETIME())

    ESCRIBIR_AUDITORIA("crear", "periodo_nomina", ALLTRIM(STR(RECCOUNT())), .T., ;
        "Periodo: " + cNom, "exito", g_cIpEstacion)
    MESSAGEBOX("Periodo creado correctamente.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC CALCULAR_PRENOMINA_MENU
*------------------------------------------------------------------------------
PROCEDURE CALCULAR_PRENOMINA_MENU
    LOCAL nPeriodoId
    nPeriodoId = VAL(INPUTBOX("ID del periodo a calcular:", "Calcular prenómina"))
    IF nPeriodoId = 0
        RETURN
    ENDIF

    SELECT periodos_nomina
    LOCATE FOR id = nPeriodoId
    IF !FOUND()
        MESSAGEBOX("Periodo no encontrado.", 16, "Error")
        RETURN
    ENDIF

    IF periodos_nomina.estado <> "abierto"
        MESSAGEBOX("Solo se puede calcular en periodos abiertos.", 16, "Error")
        RETURN
    ENDIF

    DO CALCULAR_PRENOMINA(nPeriodoId)
    MESSAGEBOX("Prenómina calculada para todos los empleados activos.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC CALCULAR_PRENOMINA - Calcula resultados para todos los empleados
*------------------------------------------------------------------------------
PROCEDURE CALCULAR_PRENOMINA(nPeriodoId)
    LOCAL dInicio, dFin, nEmpId, nDiasAsist, nFaltas, nFaltasJust, nRetardos
    LOCAL nMinRet, nSueldo, nTotalPre
    LOCAL cEstado

    SELECT periodos_nomina
    LOCATE FOR id = nPeriodoId
    dInicio = periodos_nomina.fecha_inicio
    dFin = periodos_nomina.fecha_fin

    * Borrar resultados previos del periodo (si los hay)
    SELECT resultados_nomina
    DELETE FOR periodo_nomina_id = nPeriodoId
    PACK

    SELECT empleados
    LOCATE FOR estado = "activo"
    DO WHILE !EOF()
        nEmpId = empleados.id

        * Sueldo base vigente
        nSueldo = FN_OBTENER_SUELDO_VIGENTE(nEmpId, dFin)

        * Días asistidos (días con entrada válida en el periodo)
        SELECT eventos_asistencia
        LOCATE FOR empleado_id = nEmpId ;
            AND tipo_evento = "entrada" ;
            AND resultado_validacion = "valido" ;
            AND fecha_hora >= CTOD(DTOC(dInicio)) ;
            AND fecha_hora <= CTOD(DTOC(dFin)) + 23/24 + 59/(24*60) + 59/(24*3600)
        nDiasAsist = RECCOUNT("eventos_asistencia")

        * Incidencias del periodo
        SELECT incidencias
        LOCATE FOR empleado_id = nEmpId ;
            AND fecha >= dInicio ;
            AND fecha <= dFin

        nFaltas = 0
        nFaltasJust = 0
        nRetardos = 0
        nMinRet = 0

        DO WHILE !EOF("incidencias")
            IF UPPER(incidencias.tipo_incidencia) = "FALTA"
                nFaltas = nFaltas + 1
                IF incidencias.justificada
                    nFaltasJust = nFaltasJust + 1
                ENDIF
            ELSEIF UPPER(incidencias.tipo_incidencia) = "RETARDO"
                nRetardos = nRetardos + 1
                nMinRet = nMinRet + incidencias.minutos_retardo
            ENDIF
            SKIP
        ENDDO

        nTotalPre = nSueldo  * sin descuentos automáticos

        INSERT INTO resultados_nomina (periodo_nomina_id, empleado_id, ;
                                       sueldo_base_periodo, dias_asistidos, ;
                                       faltas_registradas, faltas_justificadas, ;
                                       retardos, minutos_retardo_acumulados, ;
                                       ajustes_propuestos, ajustes_aprobados, ;
                                       total_percepciones, total_preliminar, ;
                                       estado_aprobacion, fecha_calculo) VALUES ;
            (nPeriodoId, nEmpId, nSueldo, nDiasAsist, nFaltas, nFaltasJust, ;
             nRetardos, nMinRet, 0, 0, nSueldo, nTotalPre, "pendiente", DATETIME())

        SKIP
    ENDDO

    ESCRIBIR_AUDITORIA("calcular", "prenomina", ALLTRIM(STR(nPeriodoId)), .T., ;
        "Cálculo de prenómina revisable", "exito", g_cIpEstacion)
RETURN

*------------------------------------------------------------------------------
* PROC VER_RESULTADOS_NOMINA - Muestra resultados de un periodo
*------------------------------------------------------------------------------
PROCEDURE VER_RESULTADOS_NOMINA
    LOCAL nPeriodoId
    nPeriodoId = VAL(INPUTBOX("ID del periodo:", "Ver resultados"))
    IF nPeriodoId = 0
        RETURN
    ENDIF

    SELECT resultados_nomina
    LOCATE FOR periodo_nomina_id = nPeriodoId
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC PROPONER_AJUSTE - Propone un ajuste de nómina
*------------------------------------------------------------------------------
PROCEDURE PROPONER_AJUSTE
    LOCAL nPerId, nEmpId, nConcId, nImporte, cMotivo
    nPerId = VAL(INPUTBOX("ID de periodo:", "Proponer ajuste"))
    IF nPerId = 0
        RETURN
    ENDIF
    nEmpId = VAL(INPUTBOX("ID de empleado:", "Proponer ajuste"))
    nConcId = VAL(INPUTBOX("ID de concepto:", "Proponer ajuste"))
    nImporte = VAL(INPUTBOX("Importe:", "Proponer ajuste"))
    cMotivo = INPUTBOX("Motivo:", "Proponer ajuste")

    INSERT INTO propuestas_ajuste (periodo_nomina_id, empleado_id, concepto_id, ;
                                   importe, motivo, estado, usuario_propuesta_id, ;
                                   fecha_propuesta, fecha_creacion) VALUES ;
        (nPerId, nEmpId, nConcId, nImporte, cMotivo, "propuesto", ;
         VAL(g_cUsuarioId), DATETIME(), DATETIME())

    MESSAGEBOX("Ajuste propuesto.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC DECIDIR_PROPUESTA - Aprueba o rechaza una propuesta de ajuste
*------------------------------------------------------------------------------
PROCEDURE DECIDIR_PROPUESTA
    LOCAL nPropId, cEstado
    nPropId = VAL(INPUTBOX("ID de propuesta:", "Decidir propuesta"))
    IF nPropId = 0
        RETURN
    ENDIF

    cEstado = INPUTBOX("Estado (aprobado/rechazado):", "Decidir propuesta")
    IF UPPER(cEstado) <> "APROBADO" .AND. UPPER(cEstado) <> "RECHAZADO"
        MESSAGEBOX("Estado inválido.", 16, "Error")
        RETURN
    ENDIF

    SELECT propuestas_ajuste
    LOCATE FOR id = nPropId
    IF FOUND()
        REPLACE propuestas_ajuste.estado WITH cEstado, ;
            propuestas_ajuste.usuario_aprobacion_id WITH VAL(g_cUsuarioId), ;
            propuestas_ajuste.fecha_aprobacion WITH DATETIME()

        ESCRIBIR_AUDITORIA("decidir", "propuesta_ajuste", ALLTRIM(STR(nPropId)), .T., ;
            "Propuesta " + cEstado, "exito", g_cIpEstacion)
        MESSAGEBOX("Propuesta " + cEstado + ".", 64, "OK")
    ELSE
        MESSAGEBOX("Propuesta no encontrada.", 16, "Error")
    ENDIF
RETURN

*------------------------------------------------------------------------------
* PROC CERRAR_PERIODO_MENU - Cierra un periodo de nómina
*------------------------------------------------------------------------------
PROCEDURE CERRAR_PERIODO_MENU
    LOCAL nPeriodoId
    nPeriodoId = VAL(INPUTBOX("ID del periodo a cerrar:", "Cerrar periodo"))
    IF nPeriodoId = 0
        RETURN
    ENDIF

    SELECT periodos_nomina
    LOCATE FOR id = nPeriodoId
    IF !FOUND()
        MESSAGEBOX("Periodo no encontrado.", 16, "Error")
        RETURN
    ENDIF

    IF periodos_nomina.estado = "cerrado"
        MESSAGEBOX("El periodo ya está cerrado.", 16, "Error")
        RETURN
    ENDIF

    REPLACE periodos_nomina.estado WITH "cerrado", ;
        periodos_nomina.fecha_cierre WITH DATETIME(), ;
        periodos_nomina.usuario_cierre_id WITH VAL(g_cUsuarioId)

    ESCRIBIR_AUDITORIA("cerrar", "periodo_nomina", ALLTRIM(STR(nPeriodoId)), .T., ;
        "Periodo cerrado", "exito", g_cIpEstacion)
    MESSAGEBOX("Periodo cerrado correctamente.", 64, "OK")
RETURN

RETURN