*==============================================================================
*  MAIN.PRG - Hamelin RH (Control de Asistencia, Incidencias y Prenomina)
*  Cliente: Cool Circle
*  Plataforma: Fox Dev Studio Nightly (xBase / Linux)
*  Compilacion: directamente desde terminal con el compilador xBase
*==============================================================================

SET STRICT ON
SET DATE FORMAT TO "YYYY/MM/DD"
SET CENTURY ON
SET SAFETY OFF
SET TALK OFF
SET DELETED ON

*------------------------------------------------------------------------------
*  Variables globales de sesion
*------------------------------------------------------------------------------
PUBLIC g_cUsuario   := ""
PUBLIC g_cNombre    := ""
PUBLIC g_cRol       := ""
PUBLIC g_lAdmin     := .F.
PUBLIC g_lLogueado  := .F.
PUBLIC g_cIp        := "127.0.0.1"
PUBLIC g_dHoy       := DATE()

*------------------------------------------------------------------------------
*  Punto de entrada
*------------------------------------------------------------------------------
FUNCTION Main()
    LOCAL cOpcion

    CLS
    ? "================================================"
    ? "  HAMELIN RH - Cool Circle"
    ? "  Sistema de Asistencia, Incidencias y Prenomina"
    ? "  Entorno: Fox Dev Studio Nightly (Linux xBase)"
    ? "================================================"
    WAIT "Presione una tecla para continuar..."

    DO CrearTablas
    DO VerificarPrimerAdmin

    DO WHILE .T.

        IF !g_lLogueado
            DO Login
            IF !g_lLogueado
                ? "Sesion no iniciada. Saliendo del sistema."
                WAIT
                QUIT
            ENDIF
        ENDIF

        DO MenuPrincipal

        IF !g_lLogueado
            LOOP
        ENDIF

        INPUT "Seleccione opcion: " TO cOpcion

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
            DO ModReportes
        CASE cOpcion = "8"
            DO ModAuditoria
        CASE cOpcion = "9"
            IF g_lAdmin
                DO ModUsuarios
            ELSE
                ? "Acceso restringido: solo para Administrador."
                WAIT
            ENDIF
        CASE cOpcion = "10"
            DO CerrarSesion
        CASE cOpcion = "0"
            ? "Saliendo del sistema..."
            WAIT
            QUIT
        OTHERWISE
            ? "Opcion invalida."
            WAIT
        ENDCASE
    ENDDO

    RETURN 0
ENDFUNC

*------------------------------------------------------------------------------
*  Creacion de tablas DBF si no existen
*------------------------------------------------------------------------------
PROCEDURE CrearTablas()
    LOCAL cRuta := "datos/"

    IF !FILE(cRuta + "usuarios.dbf")
        CREATE TABLE usuarios (
            username C(100),
            nombre C(200),
            email C(200),
            password C(255),
            activo L,
            intentos N,
            bloqueado D,
            ultimoc D
        )
    ENDIF

    IF !FILE(cRuta + "empleados.dbf")
        CREATE TABLE empleados (
            numero C(50),
            nombre C(100),
            apellido C(100),
            departamento C(100),
            puesto C(100),
            feching D,
            estado C(50)
        )
    ENDIF

    IF !FILE(cRuta + "asistencia.dbf")
        CREATE TABLE asistencia (
            empid C(50),
            tipo C(10),
            fechahora D,
            metodo C(50),
            resultado C(30),
            obs C(200)
        )
    ENDIF

    IF !FILE(cRuta + "incidencias.dbf")
        CREATE TABLE incidencias (
            empid C(50),
            fecha D,
            tipo C(50),
            minutos N,
            estado C(30),
            justificada L
        )
    ENDIF

    IF !FILE(cRuta + "justificantes.dbf")
        CREATE TABLE justificantes (
            empid C(50),
            tipo C(50),
            fecha D,
            estado C(30),
            fechacreacion D
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
            usuario C(100),
            fecha D,
            operacion C(50),
            entidad C(100),
            motivo C(200),
            resultado C(20)
        )
    ENDIF

    RETURN
ENDPROC

*------------------------------------------------------------------------------
*  Verificar si existe al menos un usuario (primer administrador)
*------------------------------------------------------------------------------
PROCEDURE VerificarPrimerAdmin()
    LOCAL cUser, cPass, cNom, cEmail

    USE datos/usuarios SHARED
    IF RECCOUNT() = 0
        CLOSE DATABASES

        CLS
        ? "No existe ningun usuario en el sistema."
        ? "Debe crear el PRIMER ADMINISTRADOR."
        ? ""
        INPUT "Nombre de usuario: " TO cUser
        INPUT "Contraseña: " TO cPass
        INPUT "Nombre completo: " TO cNom
        INPUT "Correo electronico: " TO cEmail

        IF EMPTY(cUser) .OR. EMPTY(cPass) .OR. EMPTY(cNom)
            ? "Datos incompletos. No se pudo crear el administrador."
            WAIT
            QUIT
        ENDIF

        USE datos/usuarios
        APPEND BLANK
        REPLACE username WITH UPPER(cUser)
        REPLACE nombre WITH cNom
        REPLACE email WITH cEmail
        REPLACE password WITH cPass   && En produccion usar hash real
        REPLACE activo WITH .T.
        REPLACE intentos WITH 0
        REPLACE bloqueado WITH CTOD("2000/01/01")
        REPLACE ultimoc WITH DATE()
        CLOSE DATABASES

        ? "Primer administrador creado correctamente."
        WAIT
    ENDIF
    CLOSE DATABASES
RETURN

*------------------------------------------------------------------------------
*  Login de usuario
*------------------------------------------------------------------------------
PROCEDURE Login()
    LOCAL cUser, cPass, cUserDb, cPassDb, lActivo, nIntentos, dBloqueo
    LOCAL nMaxInt := 5, nBloqMin := 15

    CLS
    ? "===================="
    ? "  INICIO DE SESION"
    ? "===================="
    INPUT "Usuario: " TO cUser
    INPUT "Contraseña: " TO cPass

    IF EMPTY(cUser) .OR. EMPTY(cPass)
        ? "Usuario y contraseña son obligatorios."
        WAIT
        RETURN
    ENDIF

    USE datos/usuarios SHARED

    SEEK UPPER(cUser)
    IF !FOUND()
        ? "Usuario o contraseña incorrectos."
        WAIT
        CLOSE DATABASES
        RETURN
    ENDIF

    cUserDb  := username
    cPassDb  := password
    lActivo  := activo
    nIntentos:= intentos
    dBloqueo := bloqueado

    IF !lActivo
        ? "Cuenta desactivada."
        WAIT
        CLOSE DATABASES
        RETURN
    ENDIF

    IF dBloqueo > DATE()
        ? "Cuenta bloqueada temporalmente."
        WAIT
        CLOSE DATABASES
        RETURN
    ENDIF

    IF cPass # cPassDb
        REPLACE intentos WITH nIntentos + 1
        IF nIntentos + 1 >= nMaxInt
            REPLACE bloqueado WITH CTOD(DTOC(DATE()) + STR(nBloqMin,3) + " minutes")
        ENDIF
        ? "Usuario o contraseña incorrectos."
        WAIT
        CLOSE DATABASES
        RETURN
    ENDIF

    * Autenticacion exitosa
    REPLACE intentos WITH 0
    REPLACE bloqueado WITH CTOD("2000/01/01")
    REPLACE ultimoc WITH DATE()

    g_cUsuario := cUserDb
    g_cNombre  := nombre
    g_cRol     := "Administrador"   && Simplificado para este main.prg
    g_lAdmin   := (UPPER(cUserDb) = "ADMIN")
    g_lLogueado := .T.

    DO EscribirAuditoria("login", "usuario", "Inicio de sesion exitoso")

    CLOSE DATABASES
    ? "Bienvenido, " + g_cNombre
    WAIT
RETURN

*------------------------------------------------------------------------------
*  Cerrar sesion
*------------------------------------------------------------------------------
PROCEDURE CerrarSesion()
    DO EscribirAuditoria("logout", "usuario", "Cierre de sesion")
    g_cUsuario := ""
    g_cNombre  := ""
    g_cRol     := ""
    g_lAdmin   := .F.
    g_lLogueado := .F.
    ? "Sesion cerrada."
    WAIT
RETURN

*------------------------------------------------------------------------------
*  Menu principal (dibujado en terminal)
*------------------------------------------------------------------------------
PROCEDURE MenuPrincipal()
    CLS
    ? "===================="
    ? "  MENU PRINCIPAL"
    ? "===================="
    ? "Usuario: " + g_cNombre + " (" + g_cRol + ")"
    ? ""
    ? "1. Panel de direccion"
    ? "2. Empleados"
    ? "3. Registro de asistencia"
    ? "4. Incidencias"
    ? "5. Justificantes"
    ? "6. Prenomina"
    ? "7. Reportes"
    ? "8. Auditoria"
    IF g_lAdmin
        ? "9. Usuarios y permisos"
    ENDIF
    ? "10. Cerrar sesion"
    ? "0. Salir del sistema"
    ? ""
RETURN

*------------------------------------------------------------------------------
*  Modulo: Panel de direccion (Dashboard)
*------------------------------------------------------------------------------
PROCEDURE ModDashboard()
    LOCAL nEmp, nAsis, nInc

    CLS
    ? "===================="
    ? "  PANEL DE DIRECCION"
    ? "===================="
    ? ""

    USE datos/empleados
    nEmp := RECCOUNT()
    CLOSE DATABASES

    USE datos/asistencia
    nAsis := RECCOUNT()
    CLOSE DATABASES

    USE datos/incidencias
    nInc := RECCOUNT()
    CLOSE DATABASES

    ? "Empleados registrados: " + STR(nEmp)
    ? "Eventos de asistencia:   " + STR(nAsis)
    ? "Incidencias registradas: " + STR(nInc)
    ? ""
    WAIT
RETURN

*------------------------------------------------------------------------------
*  Modulo: Empleados
*------------------------------------------------------------------------------
PROCEDURE ModEmpleados()
    LOCAL cOpcion, cNumero, cNombre, cApellido, cEstado

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  EMPLEADOS"
        ? "===================="
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
            INPUT "Numero de empleado: " TO cNumero
            INPUT "Nombre: " TO cNombre
            INPUT "Apellido: " TO cApellido
            cEstado := "activo"

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
            REPLACE feching WITH DATE()
            REPLACE estado WITH cEstado
            CLOSE DATABASES
            ? "Empleado creado."
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
*  Modulo: Asistencia
*------------------------------------------------------------------------------
PROCEDURE ModAsistencia()
    LOCAL cOpcion, cEmp, cTipo, cFecha

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  ASISTENCIA"
        ? "===================="
        ? "1. Registrar evento"
        ? "2. Listar eventos"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            INPUT "ID empleado: " TO cEmp
            INPUT "Tipo (entrada/salida): " TO cTipo
            cFecha := DTOC(DATE())

            USE datos/asistencia
            APPEND BLANK
            REPLACE empid WITH cEmp
            REPLACE tipo WITH cTipo
            REPLACE fechahora WITH DATE()
            REPLACE metodo WITH "manual"
            REPLACE resultado WITH "valido"
            REPLACE obs WITH ""
            CLOSE DATABASES
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

*------------------------------------------------------------------------------
*  Modulo: Incidencias
*------------------------------------------------------------------------------
PROCEDURE ModIncidencias()
    LOCAL cOpcion

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  INCIDENCIAS"
        ? "===================="
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

*------------------------------------------------------------------------------
*  Modulo: Justificantes
*------------------------------------------------------------------------------
PROCEDURE ModJustificantes()
    LOCAL cOpcion, cEmp, cEstado

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  JUSTIFICANTES"
        ? "===================="
        ? "1. Crear"
        ? "2. Listar pendientes"
        ? "3. Aprobar/Rechazar"
        ? "4. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            INPUT "ID empleado: " TO cEmp
            USE datos/justificantes
            APPEND BLANK
            REPLACE empid WITH cEmp
            REPLACE tipo WITH "medical"
            REPLACE fecha WITH DATE()
            REPLACE estado WITH "pendiente"
            REPLACE fechacreacion WITH DATE()
            CLOSE DATABASES
            ? "Justificante creado (pendiente)."
            WAIT
        CASE cOpcion = "2"
            USE datos/justificantes
            LIST FOR estado = "pendiente"
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "3"
            INPUT "ID justificante (numero de registro): " TO cEstado
            USE datos/justificantes
            SEEK VAL(cEstado)
            IF FOUND()
                INPUT "Estado (aprobada/rechazada): " TO cEstado
                REPLACE estado WITH cEstado
            ENDIF
            CLOSE DATABASES
        CASE cOpcion = "4"
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
*  Modulo: Prenomina
*------------------------------------------------------------------------------
PROCEDURE ModNomina()
    LOCAL cOpcion

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  PRENOMINA"
        ? "===================="
        ? "1. Crear periodo"
        ? "2. Listar periodos"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            USE datos/nomina
            APPEND BLANK
            REPLACE nombre WITH "Periodo " + DTOC(DATE())
            REPLACE finicio WITH DATE()
            REPLACE ffin WITH DATE() + 15
            REPLACE estado WITH "abierto"
            CLOSE DATABASES
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

*------------------------------------------------------------------------------
*  Modulo: Reportes
*------------------------------------------------------------------------------
PROCEDURE ModReportes()
    LOCAL cOpcion

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  REPORTES"
        ? "===================="
        ? "1. Reporte de asistencia"
        ? "2. Reporte de incidencias"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            USE datos/asistencia
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "2"
            USE datos/incidencias
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
*  Modulo: Auditoria
*------------------------------------------------------------------------------
PROCEDURE ModAuditoria()
    USE datos/auditoria
    LIST ALL
    CLOSE DATABASES
    WAIT
RETURN

*------------------------------------------------------------------------------
*  Modulo: Usuarios y permisos (solo admin)
*------------------------------------------------------------------------------
PROCEDURE ModUsuarios()
    LOCAL cOpcion

    DO WHILE .T.
        CLS
        ? "===================="
        ? "  USUARIOS (ADMIN)"
        ? "===================="
        ? "1. Listar usuarios"
        ? "2. Crear usuario"
        ? "3. Volver"
        INPUT "Opcion: " TO cOpcion

        DO CASE
        CASE cOpcion = "1"
            USE datos/usuarios
            LIST ALL
            CLOSE DATABASES
            WAIT
        CASE cOpcion = "2"
            INPUT "Usuario: " TO cOpcion
            INPUT "Contraseña: " TO cOpcion
            INPUT "Nombre: " TO cOpcion
            USE datos/usuarios
            APPEND BLANK
            REPLACE username WITH UPPER(cOpcion)
            REPLACE nombre WITH cOpcion
            REPLACE password WITH cOpcion
            REPLACE activo WITH .T.
            REPLACE intentos WITH 0
            CLOSE DATABASES
            ? "Usuario creado."
            WAIT
        CASE cOpcion = "3"
            EXIT
        ENDCASE
    ENDDO
RETURN

*------------------------------------------------------------------------------
*  Auditoria de operaciones
*------------------------------------------------------------------------------
PROCEDURE EscribirAuditoria(cOperacion, cEntidad, cMotivo)
    LOCAL cUser := IIF(EMPTY(g_cUsuario), "sistema", g_cUsuario)

    USE datos/auditoria
    APPEND BLANK
    REPLACE usuario WITH cUser
    REPLACE fecha WITH DATE()
    REPLACE operacion WITH cOperacion
    REPLACE entidad WITH cEntidad
    REPLACE motivo WITH cMotivo
    REPLACE resultado WITH "exito"
    CLOSE DATABASES
RETURN

*==============================================================================
*  Fin de main.prg
*==============================================================================