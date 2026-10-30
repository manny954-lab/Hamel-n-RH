*==============================================================================
*  CATALOGO.PRG - Departamentos, puestos, horarios y calendarios
*==============================================================================

*------------------------------------------------------------------------------
* PROC MANTENIMIENTO_DEPARTAMENTOS
*------------------------------------------------------------------------------
PROCEDURE MANTENIMIENTO_DEPARTAMENTOS
    SELECT departamentos
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC MANTENIMIENTO_PUESTOS
*------------------------------------------------------------------------------
PROCEDURE MANTENIMIENTO_PUESTOS
    SELECT puestos
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC MANTENIMIENTO_HORARIOS
*------------------------------------------------------------------------------
PROCEDURE MANTENIMIENTO_HORARIOS
    SELECT horarios
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* FN_OBTENER_HORARIO_VIGENTE - Devuelve el horario asignado a un empleado en fecha
*------------------------------------------------------------------------------
FUNCTION FN_OBTENER_HORARIO_VIGENTE(nEmpleadoId, dFecha)
    LOCAL nHorarioId
    nHorarioId = 0

    SELECT asignaciones_horario
    LOCATE FOR empleado_id = nEmpleadoId ;
        AND fecha_inicio_vigencia <= dFecha ;
        AND (fecha_fin_vigencia = .NULL. .OR. fecha_fin_vigencia >= dFecha)

    IF FOUND()
        SELECT horarios
        LOCATE FOR id = asignaciones_horario.horario_id .AND. activo = .T.
        IF FOUND()
            nHorarioId = horarios.id
        ENDIF
    ENDIF

    RETURN nHorarioId
ENDFUNC

*------------------------------------------------------------------------------
* PROC MANTENIMIENTO_CALENDARIOS
*------------------------------------------------------------------------------
PROCEDURE MANTENIMIENTO_CALENDARIOS
    SELECT calendarios_laborales
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC MENU_CATALOGOS - Menú de catálogos
*------------------------------------------------------------------------------
PROCEDURE MENU_CATALOGOS
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== CATÁLOGOS ==="
        @ 4, 10 SAY "1. Departamentos"
        @ 5, 10 SAY "2. Puestos"
        @ 6, 10 SAY "3. Horarios"
        @ 7, 10 SAY "4. Calendarios laborales"
        @ 8, 10 SAY "0. Volver"
        @ 10, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            DO MANTENIMIENTO_DEPARTAMENTOS
        CASE nOpc = 2
            DO MANTENIMIENTO_PUESTOS
        CASE nOpc = 3
            DO MANTENIMIENTO_HORARIOS
        CASE nOpc = 4
            DO MANTENIMIENTO_CALENDARIOS
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

RETURN