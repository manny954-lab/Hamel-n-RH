*==============================================================================
*  ASISTENCIA.PRG - Registro de eventos, detección de incidencias y ajustes
*==============================================================================

*------------------------------------------------------------------------------
* PROC REGISTRO_ASISTENCIA - Registro de entrada/salida de empleados
*------------------------------------------------------------------------------
PROCEDURE REGISTRO_ASISTENCIA
    LOCAL nEmpId, cTipo, dFechaHora, cMetodo, cObs
    LOCAL nResult, lOk
    nEmpId = 0
    cTipo = ""
    cMetodo = "manual"
    cObs = ""

    @ 2, 10 SAY "=== REGISTRO DE ASISTENCIA ==="
    @ 4, 10 SAY "ID de empleado:" GET nEmpId PICTURE "999999"
    @ 6, 10 SAY "Tipo (entrada/salida):" GET cTipo
    @ 8, 10 SAY "Fecha y hora:" GET dFechaHora
    @ 10, 10 SAY "Método:" GET cMetodo
    @ 12, 10 SAY "Observaciones:" GET cObs
    READ

    IF nEmpId = 0 .OR. EMPTY(cTipo)
        MESSAGEBOX("Empleado y tipo son obligatorios.", 16, "Error")
        RETURN
    ENDIF

    IF EMPTY(dFechaHora)
        dFechaHora = DATETIME()
    ENDIF

    lOk = .T.
    nResult = FN_REGISTRAR_EVENTO_ASISTENCIA(nEmpId, cTipo, dFechaHora, cMetodo, cObs)

    IF nResult > 0
        MESSAGEBOX("Evento registrado correctamente. ID: " + ALLTRIM(STR(nResult)), 64, "OK")
    ELSE
        MESSAGEBOX("Error al registrar el evento.", 16, "Error")
    ENDIF
RETURN

*------------------------------------------------------------------------------
* FN_REGISTRAR_EVENTO_ASISTENCIA - Registra evento y detecta incidencia de retardo
*------------------------------------------------------------------------------
FUNCTION FN_REGISTRAR_EVENTO_ASISTENCIA(nEmpleadoId, cTipoEvento, dFechaHora, ;
                                        cMetodoRegistro, cObservaciones)
    LOCAL nEventoId, cResultado, nHorarioId, nMinRet
    LOCAL dInicioDia, dFinDia, lExisteEntrada
    LOCAL cRegla

    * Verificar empleado existe y está activo
    SELECT empleados
    LOCATE FOR id = nEmpleadoId
    IF !FOUND()
        RETURN 0
    ENDIF
    IF empleados.estado <> "activo"
        RETURN 0
    ENDIF

    * Detectar duplicado (mismo minuto)
    SELECT eventos_asistencia
    LOCATE FOR empleado_id = nEmpleadoId ;
        AND tipo_evento = cTipoEvento ;
        AND fecha_hora = CTOD(DTOC(dFechaHora) + TIME(dFechaHora))  && mismo minuto aproximado
    IF FOUND()
        cResultado = "duplicado"
    ELSE
        cResultado = "valido"
    ENDIF

    * Si es salida, verificar que exista entrada previa el mismo día
    IF cTipoEvento = "salida"
        dInicioDia = CTOD(DTOC(dFechaHora))
        dFinDia = dInicioDia + 1
        SELECT eventos_asistencia
        LOCATE FOR empleado_id = nEmpleadoId ;
            AND tipo_evento = "entrada" ;
            AND fecha_hora >= dInicioDia ;
            AND fecha_hora < dFinDia ;
            AND fecha_hora < dFechaHora
        IF !FOUND()
            cResultado = "imposible"
        ENDIF
    ENDIF

    * Insertar evento
    INSERT INTO eventos_asistencia (empleado_id, tipo_evento, fecha_hora, ;
                                    metodo_registro, resultado_validacion, ;
                                    observaciones, usuario_registro_id, ;
                                    fecha_creacion) VALUES ;
        (nEmpleadoId, cTipoEvento, dFechaHora, cMetodoRegistro, cResultado, ;
         cObservaciones, VAL(g_cUsuarioId), DATETIME())

    nEventoId = RECCOUNT("eventos_asistencia")

    * Si es entrada válida, calcular retardo
    IF cResultado = "valido" .AND. cTipoEvento = "entrada"
        nHorarioId = FN_OBTENER_HORARIO_VIGENTE(nEmpleadoId, CTOD(DTOC(dFechaHora)))
        IF nHorarioId > 0
            SELECT horarios
            LOCATE FOR id = nHorarioId
            IF FOUND()
                IF FN_FECHA_ES_LABORABLE(CTOD(DTOC(dFechaHora)), nHorarioId)
                    cRegla = ""
                    nMinRet = FN_CALCULAR_RETARDO(dFechaHora, horarios.hora_entrada, ;
                                                   horarios.tolerancia_minutos, @cRegla)
                    IF nMinRet > 0
                        INSERT INTO incidencias (empleado_id, evento_asistencia_id, fecha, ;
                                                 tipo_incidencia, minutos_retardo, ;
                                                 tiempo_incidencia_minutos, regla_aplicada, ;
                                                 justificada, estado, fecha_creacion) VALUES ;
                         (nEmpleadoId, nEventoId, CTOD(DTOC(dFechaHora)), "retardo", ;
                          nMinRet, nMinRet, cRegla, .F., "pendiente", DATETIME())

                        REPLACE eventos_asistencia.incidencia_detectada WITH .T. ;
                             IN eventos_asistencia
                    ENDIF
                ENDIF
            ENDIF
        ENDIF
    ENDIF

    ESCRIBIR_AUDITORIA("crear", "evento_asistencia", ALLTRIM(STR(nEventoId)), .T., ;
        cTipoEvento + " " + DTOC(dFechaHora) + " resultado=" + cResultado, "exito", g_cIpEstacion)

    RETURN nEventoId
ENDFUNC

*------------------------------------------------------------------------------
* FN_CALCULAR_RETARDO - Calcula minutos de retardo respecto a hora de entrada
*------------------------------------------------------------------------------
FUNCTION FN_CALCULAR_RETARDO(dFechaHora, tEntrada, nTolerancia, @cRegla)
    LOCAL nMinutos, tLimite, lFuera
    LOCAL dEntrada, dReal

    nMinutos = 0
    cRegla = ""

    dEntrada = CTOD(DTOC(dFechaHora) + TTOC(tEntrada))
    dReal = dFechaHora

    * Límite = entrada + tolerancia
    tLimite = tEntrada + (nTolerancia / 1440)

    IF dReal > CTOD(DTOC(dFechaHora) + TTOC(tLimite))
        lFuera = .T.
        nMinutos = FN_MINUTOS_ENTRE(dEntrada, dReal)
        cRegla = "Retardo: entrada supera horario + tolerancia"
    ENDIF

    RETURN nMinutos
ENDFUNC

*------------------------------------------------------------------------------
* PROC LISTAR_EVENTOS - Muestra eventos de asistencia
*------------------------------------------------------------------------------
PROCEDURE LISTAR_EVENTOS
    SELECT eventos_asistencia
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC CORREGIR_EVENTO - Corrige un evento generando ajuste auditable
*------------------------------------------------------------------------------
PROCEDURE CORREGIR_EVENTO
    LOCAL nEvtId, cTipo, dFecHora, cObs, cMotivo
    LOCAL cAnt, cNuevo

    nEvtId = VAL(INPUTBOX("ID del evento a corregir:", "Corregir evento"))
    IF nEvtId = 0
        RETURN
    ENDIF

    SELECT eventos_asistencia
    LOCATE FOR id = nEvtId
    IF !FOUND()
        MESSAGEBOX("Evento no encontrado.", 16, "Error")
        RETURN
    ENDIF

    cAnt = "tipo=" + eventos_asistencia.tipo_evento + ;
           ", fecha=" + DTOC(eventos_asistencia.fecha_hora) + ;
           ", obs=" + ALLTRIM(eventos_asistencia.observaciones)

    cTipo = INPUTBOX("Nuevo tipo (entrada/salida):", "Corregir", ;
                     eventos_asistencia.tipo_evento)
    dFecHora = CTOD(INPUTBOX("Nueva fecha y hora:", "Corregir", ;
                 DTOC(eventos_asistencia.fecha_hora)))
    cObs = INPUTBOB("Nueva observación:", "Corregir", ;
            ALLTRIM(eventos_asistencia.observaciones))
    cMotivo = INPUTBOX("Motivo de la corrección:", "Corregir")

    cNuevo = "tipo=" + cTipo + ", fecha=" + DTOC(dFecHora) + ", obs=" + cObs

    INSERT INTO ajustes_asistencia (evento_asistencia_id, valor_anterior, valor_corregido, ;
                                    motivo, fecha_ajuste, usuario_responsable_id) VALUES ;
        (nEvtId, cAnt, cNuevo, cMotivo, DATETIME(), VAL(g_cUsuarioId))

    REPLACE eventos_asistencia.tipo_evento WITH cTipo, ;
        eventos_asistencia.fecha_hora WITH dFecHora, ;
        eventos_asistencia.observaciones WITH cObs

    ESCRIBIR_AUDITORIA("ajustar", "evento_asistencia", ALLTRIM(STR(nEvtId)), .T., ;
        cMotivo, "exito", g_cIpEstacion)
    MESSAGEBOX("Evento corregido y ajuste registrado.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC PENDIENTES_SALIDA - Muestra entradas sin salida
*------------------------------------------------------------------------------
PROCEDURE PENDIENTES_SALIDA
    LOCAL dDesde
    dDesde = DATE() - 30

    SELECT eventos_asistencia
    LOCATE FOR tipo_evento = "entrada" ;
        AND fecha_hora >= dDesde

    BROWSE NORMAL NOWAIT
RETURN

RETURN