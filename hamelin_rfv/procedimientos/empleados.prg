*==============================================================================
*  EMPLEADOS.PRG - Empleados, configuración salarial y asignaciones
*==============================================================================

*------------------------------------------------------------------------------
* PROC MANTENIMIENTO_EMPLEADOS - CRUD de empleados
*------------------------------------------------------------------------------
PROCEDURE MANTENIMIENTO_EMPLEADOS
    LOCAL nOpc
    nOpc = 0
    DO WHILE .T.
        CLEAR
        @ 2, 10 SAY "=== EMPLEADOS ==="
        @ 4, 10 SAY "1. Listar empleados"
        @ 5, 10 SAY "2. Crear empleado"
        @ 6, 10 SAY "3. Editar empleado"
        @ 7, 10 SAY "4. Configuración salarial"
        @ 8, 10 SAY "5. Asignar horario"
        @ 9, 10 SAY "0. Volver"
        @ 11, 10 GET nOpc PICTURE "9"
        READ

        DO CASE
        CASE nOpc = 1
            SELECT empleados
            BROWSE NORMAL NOWAIT
        CASE nOpc = 2
            DO CREAR_EMPLEADO
        CASE nOpc = 3
            DO EDITAR_EMPLEADO
        CASE nOpc = 4
            DO CONFIG_SALARIAL
        CASE nOpc = 5
            DO ASIGNAR_HORARIO_EMP
        CASE nOpc = 0
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE CREAR_EMPLEADO
    LOCAL cNum, cNom, cApeP, cApeM, nDepto, nPuesto, dIng, cEstado
    cNum = SPACE(50)
    cNom = SPACE(100)
    cApeP = SPACE(100)
    cApeM = SPACE(100)
    dIng = DATE()
    cEstado = "activo"

    @ 2, 10 SAY "Número de empleado:" GET cNum
    @ 4, 10 SAY "Nombre:" GET cNom
    @ 6, 10 SAY "Apellido paterno:" GET cApeP
    @ 8, 10 SAY "Apellido materno:" GET cApeM
    @ 10, 10 SAY "Fecha ingreso:" GET dIng
    @ 12, 10 SAY "Estado:" GET cEstado
    READ

    IF EMPTY(cNum) .OR. EMPTY(cNom) .OR. EMPTY(cApeP)
        MESSAGEBOX("Campos obligatorios: número, nombre, apellido paterno.", 16, "Error")
        RETURN
    ENDIF

    SELECT empleados
    LOCATE FOR UPPER(numero_empleado) = UPPER(cNum)
    IF FOUND()
        MESSAGEBOX("El número de empleado ya existe.", 16, "Error")
        RETURN
    ENDIF

    INSERT INTO empleados (numero_empleado, nombre, apellido_paterno, apellido_materno, ;
                           fecha_ingreso, estado, fecha_creacion) VALUES ;
        (cNum, cNom, cApeP, cApeM, dIng, cEstado, DATETIME())

    ESCRIBIR_AUDITORIA("crear", "empleado", ALLTRIM(STR(RECCOUNT())), .T., ;
        "Empleado creado: " + cNom, "exito", g_cIpEstacion)
    MESSAGEBOX("Empleado creado correctamente.", 64, "OK")
RETURN

PROCEDURE EDITAR_EMPLEADO
    LOCAL nId, cNom, cApeP, cApeM, cEstado
    nId = VAL(INPUTBOX("ID de empleado a editar:", "Editar empleado"))
    IF nId = 0
        RETURN
    ENDIF

    SELECT empleados
    LOCATE FOR id = nId
    IF !FOUND()
        MESSAGEBOX("Empleado no encontrado.", 16, "Error")
        RETURN
    ENDIF

    cNom = empleados.nombre
    cApeP = empleados.apellido_paterno
    cApeM = empleados.apellido_materno
    cEstado = empleados.estado

    @ 2, 10 SAY "Nombre:" GET cNom
    @ 4, 10 SAY "Apellido paterno:" GET cApeP
    @ 6, 10 SAY "Apellido materno:" GET cApeM
    @ 8, 10 SAY "Estado:" GET cEstado
    READ

    REPLACE nombre WITH cNom, apellido_paterno WITH cApeP, ;
        apellido_materno WITH cApeM, estado WITH cEstado, ;
        fecha_modificacion WITH DATETIME()
    MESSAGEBOX("Empleado actualizado.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC CONFIG_SALARIAL - Configuración salarial de un empleado
*------------------------------------------------------------------------------
PROCEDURE CONFIG_SALARIAL
    LOCAL nEmpId, nSueldo, cPeriodicidad, dVig
    nEmpId = VAL(INPUTBOX("ID de empleado:", "Configuración salarial"))
    IF nEmpId = 0
        RETURN
    ENDIF

    nSueldo = VAL(INPUTBOX("Sueldo base:", "Configuración salarial"))
    cPeriodicidad = INPUTBOX("Periodicidad (quincenal/mensual):", "Configuración salarial")
    dVig = DATE()

    INSERT INTO configuracion_salarial (empleado_id, sueldo_base, periodicidad, ;
                                        fecha_vigencia, fecha_creacion) VALUES ;
        (nEmpId, nSueldo, cPeriodicidad, dVig, DATETIME())
    MESSAGEBOX("Configuración salarial guardada.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* PROC ASIGNAR_HORARIO_EMP - Asigna horario a un empleado con vigencia
*------------------------------------------------------------------------------
PROCEDURE ASIGNAR_HORARIO_EMP
    LOCAL nEmpId, nHorId, dInicio, dFin
    nEmpId = VAL(INPUTBOX("ID de empleado:", "Asignar horario"))
    IF nEmpId = 0
        RETURN
    ENDIF

    nHorId = VAL(INPUTBOX("ID de horario:", "Asignar horario"))
    dInicio = DATE()
    dFin = CTOD(INPUTBOX("Fecha fin vigencia (opcional, dejar vacío para indefinido):", "Asignar horario"))

    INSERT INTO asignaciones_horario (empleado_id, horario_id, fecha_inicio_vigencia, ;
                                      fecha_fin_vigencia, fecha_creacion) VALUES ;
        (nEmpId, nHorId, dInicio, IIF(EMPTY(dFin), .NULL., dFin), DATETIME())
    MESSAGEBOX("Horario asignado.", 64, "OK")
RETURN

*------------------------------------------------------------------------------
* FN_OBTENER_SUELDO_VIGENTE - Devuelve el sueldo base vigente de un empleado en fecha
*------------------------------------------------------------------------------
FUNCTION FN_OBTENER_SUELDO_VIGENTE(nEmpleadoId, dFechaFin)
    LOCAL nSueldo
    nSueldo = 0

    SELECT configuracion_salarial
    LOCATE FOR empleado_id = nEmpleadoId ;
        AND fecha_vigencia <= dFechaFin ;
        AND (fecha_fin_vigencia = .NULL. .OR. fecha_fin_vigencia >= CTOD(DTOC(dFechaFin) - 30))
    ORDER BY fecha_vigencia DESC

    IF FOUND()
        nSueldo = configuracion_salarial.sueldo_base
    ENDIF

    RETURN nSueldo
ENDFUNC

RETURN