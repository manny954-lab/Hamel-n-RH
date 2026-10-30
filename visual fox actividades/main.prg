*------------------------------------------------------------------------------
* MAIN.PRG - Hamelin RH Minimal (xBase / Fox Dev Studio Nightly)
* Sin login. Funciones basicas.
*------------------------------------------------------------------------------

SET STRICT ON
SET CENTURY ON
SET SAFETY OFF
SET TALK OFF
SET DELETED ON

PUBLIC g_cUsuario
PUBLIC g_cNombre
PUBLIC g_lLogueado

g_cUsuario  = ""
g_cNombre   = "Visitante"
g_lLogueado = .T.

FUNCTION Main
    LOCAL cOpcion

    CLS
    ? "========================================"
    ? "  HAMELIN RH - Cool Circle"
    ? "  Modo minimalista - Fox Dev Studio"
    ? "========================================"
    WAIT "Presione una tecla..."

    DO CrearTablas

    DO WHILE .T.
        DO MenuPrincipal
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            DO ModDashboard
        CASE cOpcion = "2"
            DO ModEmpleados
        CASE cOpcion = "3"
            DO ModAsistencia
        CASE cOpcion = "4"
            DO ModIncidencias
        CASE cOpcion = "5"
            DO ModJustificantes
        CASE cOpcion = "6"
            DO ModNomina
        CASE cOpcion = "7"
            DO ModAuditoria
        CASE cOpcion = "0"
            ? "Saliendo..."
            WAIT
            QUIT
        OTHERWISE
            ? "Opcion invalida."
            WAIT
        ENDCASE
    ENDDO

    RETURN
ENDFUNC

PROCEDURE CrearTablas
    LOCAL cRuta
    cRuta = "datos/"

    IF !FILE(cRuta + "usuarios.dbf")
        CREATE TABLE usuarios (
            username C(100),
            nombre C(200),
            activo L
        )
    ENDIF

    IF !FILE(cRuta + "empleados.dbf")
        CREATE TABLE empleados (
            numero C(50),
            nombre C(100),
            apellido C(100),
            estado C(50)
        )
    ENDIF

    IF !FILE(cRuta + "asistencia.dbf")
        CREATE TABLE asistencia (
            empid C(50),
            tipo C(10),
            fechahora D,
            resultado C(30)
        )
    ENDIF

    IF !FILE(cRuta + "incidencias.dbf")
        CREATE TABLE incidencias (
            empid C(50),
            fecha D,
            tipo C(50),
            estado C(30)
        )
    ENDIF

    IF !FILE(cRuta + "justificantes.dbf")
        CREATE TABLE justificantes (
            empid C(50),
            tipo C(50),
            fecha D,
            estado C(30)
        )
    ENDIF

    IF !FILE(cRuta + "nomina.dbf")
        CREATE TABLE nomina (
            nombre C(150),
            finicio D,
            ffin D,
            estado C(30)
        )
    ENDIF

    IF !FILE(cRuta + "auditoria.dbf")
        CREATE TABLE auditoria (
            fecha D,
            operacion C(50),
            entidad C(100),
            motivo C(200)
        )
    ENDIF

RETURN

PROCEDURE EscribirAuditoria(cOperacion, cEntidad, cMotivo)
    USE datos/auditoria
    APPEND BLANK
    REPLACE fecha WITH DATE()
    REPLACE operacion WITH cOperacion
    REPLACE entidad WITH cEntidad
    REPLACE motivo WITH cMotivo
    CLOSE DATABASES
RETURN

PROCEDURE MenuPrincipal
    CLS
    ? "===================="
    ? "  MENU PRINCIPAL"
    ? "===================="
    ? "Usuario: " + g_cNombre
    ? ""
    ? "1. Panel de direccion"
    ? "2. Empleados"
    ? "3. Asistencia"
    ? "4. Incidencias"
    ? "5. Justificantes"
    ? "6. Prenomina"
    ? "7. Auditoria"
    ? "0. Salir"
    ? ""
RETURN

PROCEDURE ModDashboard
    LOCAL nEmp, nAsis, nInc

    CLS
    ? "--- PANEL DE DIRECCION ---"
    ? ""

    USE datos/empleados
    nEmp = RECCOUNT()
    CLOSE DATABASES

    USE datos/asistencia
    nAsis = RECCOUNT()
    CLOSE DATABASES

    USE datos/incidencias
    nInc = RECCOUNT()
    CLOSE DATABASES

    ? "Empleados:   " + STR(nEmp)
    ? "Asistencia:  " + STR(nAsis)
    ? "Incidencias: " + STR(nInc)
    ? ""
    WAIT
RETURN

PROCEDURE ModEmpleados
    LOCAL cOpcion, cNumero, cNombre, cApellido

    DO WHILE .T.
        CLS
        ? "--- EMPLEADOS ---"
        ? "1. Listar"
        ? "2. Crear"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            USE datos/empleados
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "2"
            INPUT "Numero: " TO cNumero
            INPUT "Nombre: " TO cNombre
            INPUT "Apellido: " TO cApellido

            IF EMPTY(cNumero) .OR. EMPTY(cNombre)
                ? "Datos incompletos."
                WAIT
                LOOP
            ENDIF

            USE datos/empleados
            APPEND BLANK
            REPLACE numero WITH cNumero
            REPLACE nombre WITH cNombre
            REPLACE apellido WITH cApellido
            REPLACE estado WITH "activo"
            CLOSE DATABASES

            DO EscribirAuditoria("crear", "empleado", cNumero + " " + cNombre)
            ? "Empleado creado."
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE ModAsistencia
    LOCAL cOpcion, cEmp, cTipo

    DO WHILE .T.
        CLS
        ? "--- ASISTENCIA ---"
        ? "1. Registrar evento"
        ? "2. Listar eventos"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            INPUT "ID empleado: " TO cEmp
            INPUT "Tipo (entrada/salida): " TO cTipo

            USE datos/asistencia
            APPEND BLANK
            REPLACE empid WITH cEmp
            REPLACE tipo WITH cTipo
            REPLACE fechahora WITH DATE()
            REPLACE resultado WITH "valido"
            CLOSE DATABASES

            DO EscribirAuditoria("crear", "asistencia", cTipo + " " + cEmp)
            ? "Evento registrado."
            WAIT
        CASE cOpcion = "2"
            USE datos/asistencia
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE ModIncidencias
    LOCAL cOpcion

    DO WHILE .T.
        CLS
        ? "--- INCIDENCIAS ---"
        ? "1. Listar"
        ? "2. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            USE datos/incidencias
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "2"
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE ModJustificantes
    LOCAL cOpcion, cEmp, cTipo

    DO WHILE .T.
        CLS
        ? "--- JUSTIFICANTES ---"
        ? "1. Crear"
        ? "2. Listar"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            INPUT "ID empleado: " TO cEmp
            INPUT "Tipo: " TO cTipo

            USE datos/justificantes
            APPEND BLANK
            REPLACE empid WITH cEmp
            REPLACE tipo WITH cTipo
            REPLACE fecha WITH DATE()
            REPLACE estado WITH "pendiente"
            CLOSE DATABASES

            DO EscribirAuditoria("crear", "justificante", cTipo + " " + cEmp)
            ? "Justificante creado."
            WAIT
        CASE cOpcion = "2"
            USE datos/justificantes
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE ModNomina
    LOCAL cOpcion, cNombre

    DO WHILE .T.
        CLS
        ? "--- PRENOMINA ---"
        ? "1. Crear periodo"
        ? "2. Listar periodos"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            INPUT "Nombre periodo: " TO cNombre

            USE datos/nomina
            APPEND BLANK
            REPLACE nombre WITH cNombre
            REPLACE finicio WITH DATE()
            REPLACE ffin WITH DATE() + 15
            REPLACE estado WITH "abierto"
            CLOSE DATABASES

            DO EscribirAuditoria("crear", "nomina", cNombre)
            ? "Periodo creado."
            WAIT
        CASE cOpcion = "2"
            USE datos/nomina
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

PROCEDURE ModAuditoria
    USE datos/auditoria
    LIST ALL
    CLOSE DATABASES
    WAIT
RETURN
