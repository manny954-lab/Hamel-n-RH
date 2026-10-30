*==============================================================================
*  MENUS.PRG - Definición de menús y dispatchers por módulo
*==============================================================================

*------------------------------------------------------------------------------
* PROC DASHBOARD - Panel de dirección con métricas básicas
*------------------------------------------------------------------------------
PROCEDURE DASHBOARD
    LOCAL nEmpleados, nEventosHoy, nIncidenciasPend, nPeriodosAbiertos
    LOCAL nJustPend

    SELECT empleados
    nEmpleados = RECCOUNT()

    SELECT eventos_asistencia
    LOCATE FOR fecha_hora >= CTOD(DTOC(DATE()))
    nEventosHoy = RECCOUNT()

    SELECT incidencias
    LOCATE FOR estado = "pendiente"
    nIncidenciasPend = RECCOUNT()

    SELECT periodos_nomina
    LOCATE FOR estado = "abierto"
    nPeriodosAbiertos = RECCOUNT()

    SELECT justificantes
    LOCATE FOR estado = "pendiente"
    nJustPend = RECCOUNT()

    CLEAR
    @ 2, 10 SAY "=== PANEL DE DIRECCIÓN ===" FONT "Arial", 14, BOLD
    @ 4, 10 SAY "Empleados registrados:      " + ALLTRIM(STR(nEmpleados))
    @ 5, 10 SAY "Eventos de asistencia hoy:  " + ALLTRIM(STR(nEventosHoy))
    @ 6, 10 SAY "Incidencias pendientes:     " + ALLTRIM(STR(nIncidenciasPend))
    @ 7, 10 SAY "Justificantes pendientes:   " + ALLTRIM(STR(nJustPend))
    @ 8, 10 SAY "Periodos de nómina abiertos:" + ALLTRIM(STR(nPeriodosAbiertos))
    @ 10, 10 SAY "Presione cualquier tecla para volver..."
    WAIT CLEAR
RETURN

*------------------------------------------------------------------------------
* PROC MENU_REPORTES - Reportes del sistema
*------------------------------------------------------------------------------
PROCEDURE MENU_REPORTES
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== REPORTES ==="
        @ 4, 10 SAY "1. Reporte de asistencia"
        @ 5, 10 SAY "2. Reporte de incidencias"
        @ 6, 10 SAY "3. Reporte de nómina"
        @ 7, 10 SAY "4. Reporte de auditoría"
        @ 8, 10 SAY "0. Volver"
        @ 10, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            DO REPORTE_ASISTENCIA
        CASE nOpc = 2
            DO REPORTE_INCIDENCIAS
        CASE nOpc = 3
            DO REPORTE_NOMINA
        CASE nOpc = 4
            DO REPORTE_AUDITORIA
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE REPORTE_ASISTENCIA
    SELECT eventos_asistencia
    BROWSE NORMAL NOWAIT
RETURN

PROCEDURE REPORTE_INCIDENCIAS
    SELECT incidencias
    BROWSE NORMAL NOWAIT
RETURN

PROCEDURE REPORTE_NOMINA
    SELECT resultados_nomina
    BROWSE NORMAL NOWAIT
RETURN

PROCEDURE REPORTE_AUDITORIA
    SELECT auditoria
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC MENU_AUDITORIA - Visualizador de auditoría
*------------------------------------------------------------------------------
PROCEDURE MENU_AUDITORIA
    SELECT auditoria
    BROWSE NORMAL NOWAIT
RETURN

*------------------------------------------------------------------------------
* PROC PROCESAR_OPCION_MENU - Dispatcher del menú principal (referencia desde MAIN.PRG)
*------------------------------------------------------------------------------
PROCEDURE PROCESAR_OPCION_MENU(nOpcion)
    DO CASE
        CASE nOpcion = 1
            DO DASHBOARD
        CASE nOpcion = 2
            DO MANTENIMIENTO_EMPLEADOS
        CASE nOpcion = 3
            DO REGISTRO_ASISTENCIA
        CASE nOpcion = 4
            DO GESTION_INCIDENCIAS
        CASE nOpcion = 5
            DO GESTION_JUSTIFICANTES
        CASE nOpcion = 6
            DO GESTION_NOMINA
        CASE nOpcion = 7
            DO MENU_REPORTES
        CASE nOpcion = 8
            DO MENU_AUDITORIA
        CASE nOpcion = 9
            IF g_lAdmin
                DO MENU_USUARIOS
            ELSE
                MESSAGEBOX("Acceso restringido: módulo solo para el Administrador del sistema.", 48, "Acceso denegado")
            ENDIF
        CASE nOpcion = 10
            DO CERRAR_SESION_USUARIO
        CASE nOpcion = 11
            g_nModuloActivo = 0
    ENDCASE
RETURN

*------------------------------------------------------------------------------
* PROC GESTION_INCIDENCIAS - Gestión de incidencias
*------------------------------------------------------------------------------
PROCEDURE GESTION_INCIDENCIAS
    SELECT incidencias
    BROWSE NORMAL NOWAIT
RETURN

RETURN