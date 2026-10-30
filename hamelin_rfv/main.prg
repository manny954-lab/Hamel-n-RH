*==============================================================================
*  HAMÉLIN RH - Sistema de Control de Asistencia, Incidencias y Prenómina
*  Cliente: Cool Circle
*  Plataforma: Visual FoxPro 9.0
*  Archivo: MAIN.PRG  (punto de entrada / arranque del sistema)
*==============================================================================
*  Rehacer desde cero (no traducción línea por línea del proyecto Python),
*  adaptado a los patrones nativos de VFP: archivos .PRG, PROCEDURE/FUNCTION,
*  tablas DBF dentro de un contenedor DBC y menú de módulos.
*==============================================================================

#INCLUDE "AFX.H"

*------------------------------------------------------------------------------
* 1. CONFIGURACIÓN DE ENTORNO VFP
*------------------------------------------------------------------------------
SET STRICT ON
SET EXACT OFF
SET DATE ANSI
SET CENTURY ON
SET SAFETY OFF
SET TALK OFF
SET NOTIFY OFF
SET DELETED ON
SET EXCLUSIVE OFF
SET AUTOORDER ON
SET REPROCESS TO 2
SET CURSOR OFF
SET MESSAGE TO STATUS

*------------------------------------------------------------------------------
* 2. RUTAS DE TRABAJO (relativas al directorio del ejecutable .APP/.EXE)
*------------------------------------------------------------------------------
SET PATH TO datos\;procedimientos\;formularios\;informes\

*------------------------------------------------------------------------------
* 3. VARIABLES PÚBLICAS DE SESIÓN GLOBAL
*------------------------------------------------------------------------------
PUBLIC g_nSesionId      && ID de sesión activa (numérico)
PUBLIC g_cUsuarioId     && ID del usuario logueado (caracter, simula UUID)
PUBLIC g_cUsername      && Nombre de usuario
PUBLIC g_cUsuarioNom    && Nombre completo del usuario
PUBLIC g_cRolNom        && Rol asignado al usuario
PUBLIC g_lAdmin         && .T. si es Administrador del sistema
PUBLIC g_cIpEstacion    && Dirección IP de la estación
PUBLIC g_dFechaSistema  && Fecha del sistema
PUBLIC g_cRutaDatos     && Ruta a la carpeta de datos
PUBLIC g_cRutaProcs     && Ruta a los procedimientos
PUBLIC g_nModuloActivo  && Módulo del menú actualmente abierto (0 = salir)
PUBLIC g_lSesionValida  && .T. si hay sesión válida

*------------------------------------------------------------------------------
* 4. CONSTANTES GLOBALES
*------------------------------------------------------------------------------
#DEFINE ESTADO_PENDIENTE   "pendiente"
#DEFINE ESTADO_EN_REVISION "en_revision"
#DEFINE ESTADO_APROBADA    "aprobada"
#DEFINE ESTADO_RECHAZADA   "rechazada"
#DEFINE ESTADO_CERRADO     "cerrado"
#DEFINE ESTADO_ABIERTO     "abierto"
#DEFINE ESTADO_ACTIVO      "activo"
#DEFINE ESTADO_INACTIVO    "inactivo"

#DEFINE EVENTO_ENTRADA  "entrada"
#DEFINE EVENTO_SALIDA   "salida"

#DEFINE MSG_LOGIN_INVALID   "Usuario o contraseña incorrectos."
#DEFINE MSG_CUENTA_BLOQUEADA "Cuenta bloqueada temporalmente. Intente más tarde."
#DEFINE MSG_ACCESO_RESTRINGIDO "Acceso restringido: módulo solo para el Administrador del sistema."

*------------------------------------------------------------------------------
* 5. INICIALIZACIÓN DEL SISTEMA
*------------------------------------------------------------------------------
DO DECLARACIONES
DO INICIALIZAR_ENTORNO
DO CARGAR_PROCEDIMIENTOS
DO CREAR_O_ABRIR_BASE_DATOS
DO VERIFICAR_PRIMER_ADMIN

*------------------------------------------------------------------------------
* 6. BUCLE PRINCIPAL (sesión -> menú -> módulos -> logout)
*------------------------------------------------------------------------------
DO WHILE .T.

    *--- Si no hay sesión válida, mostrar pantalla de login
    IF !g_lSesionValida
        DO PANTALLA_LOGIN
        IF !g_lSesionValida
            * El usuario canceló el login -> terminar aplicación
            EXIT
        ENDIF
    ENDIF

    *--- Desplegar menú principal y obtener opción
    DO MENU_PRINCIPAL

    *--- Despachar la opción seleccionada (definido en menus.prg)
    DO PROCESAR_OPCION_MENU(g_nModuloActivo)

    *--- Si se cerró la sesión, volver al inicio del bucle (login)
    IF !g_lSesionValida
        LOOP
    ENDIF

    *--- Si el menú devolvió 0, el usuario eligió salir del sistema
    IF g_nModuloActivo = 0
        EXIT
    ENDIF

ENDDO

DO CIERRAR_SISTEMA
QUIT

*==============================================================================
* 7. PROCEDIMIENTOS LOCALES DE MAIN.PRG
*==============================================================================

PROCEDURE DECLARACIONES
    * Inicializa todas las variables públicas de sesión
    g_nSesionId      = 0
    g_cUsuarioId     = ""
    g_cUsername      = ""
    g_cUsuarioNom    = ""
    g_cRolNom        = ""
    g_lAdmin         = .F.
    g_cIpEstacion    = "127.0.0.1"
    g_dFechaSistema  = DATE()
    g_cRutaDatos     = ADDBS(JUSTPATH(SYS(2003))) + "datos\"
    g_cRutaProcs     = ADDBS(JUSTPATH(SYS(2003))) + "procedimientos\"
    g_nModuloActivo  = 0
    g_lSesionValida  = .F.
RETURN

PROCEDURE INICIALIZAR_ENTORNO
    * Configuración adicional de la sesión VFP
    SET STATUS BAR TO "Hamelín RH - Cool Circle  |  v1.0.0  |  Visual FoxPro 9.0"
RETURN

PROCEDURE CARGAR_PROCEDIMIENTOS
    * Carga todas las bibliotecas de procedimientos (.PRG) de forma aditiva.
    * Cada biblioteca agrupa PROCEDURE/FUNCTION por dominio de negocio.
    SET PROCEDURE TO (g_cRutaProcs + "util.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "seguridad.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "catalogo.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "empleados.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "asistencia.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "justificantes.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "nomina.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "auditoria.prg") ADDITIVE
    SET PROCEDURE TO (g_cRutaProcs + "menus.prg") ADDITIVE
RETURN

PROCEDURE CREAR_O_ABRIR_BASE_DATOS
    * Abre o crea el contenedor de base de datos HAMILIN.DBC.
    * Si no existe, crea las tablas y los datos semilla.
    LOCAL cDbc, cRutaDbc
    cDbc = "HAMILIN"
    cRutaDbc = g_cRutaDatos + cDbc + ".DBC"

    IF FILE(cRutaDbc)
        SET DATABASE TO (cRutaDbc)
    ELSE
        CREATE DATABASE (cRutaDbc)
        SET DATABASE TO (cRutaDbc)
        DO CREAR_TABLAS
        DO POBLAR_DATOS_BASE
    ENDIF

    DO ABRIR_TABLAS_SISTEMA
RETURN

PROCEDURE CREAR_TABLAS
    * Crea todas las tablas .DBF dentro del contenedor DBC.
    * Esquema equivalente al modelo SQLAlchemy/Alembic del proyecto Python.

    *** Tablas de configuración y catálogos ***
    CREATE TABLE configuracion (
        id I PRIMARY KEY AUTOINCREMENT,
        clave C(100) UNIQUE,
        valor M,
        descripcion C(500),
        fecha_creacion T,
        fecha_modificacion T
    )
    CREATE TAG cfg_clave ON configuracion TAG cfg_clave FOR UPPER(clave) COMPACT

    CREATE TABLE departamentos (
        id I PRIMARY KEY AUTOINCREMENT,
        codigo C(50) UNIQUE,
        nombre C(150),
        activo L DEFAULT .T.
    )
    CREATE TAG dep_codigo ON departamentos TAG dep_codigo FOR UPPER(codigo) COMPACT
    CREATE TAG dep_activo ON departamentos TAG dep_activo FOR activo COMPACT

    CREATE TABLE puestos (
        id I PRIMARY KEY AUTOINCREMENT,
        codigo C(50) UNIQUE,
        nombre C(150),
        departamento_id I,
        activo L DEFAULT .T.
    )
    CREATE TAG pue_codigo ON puestos TAG pue_codigo FOR UPPER(codigo) COMPACT
    CREATE INDEX pue_depto ON puestos TAG pue_depto FOR departamento_id COMPACT

    CREATE TABLE calendarios_laborales (
        id I PRIMARY KEY AUTOINCREMENT,
        nombre C(150),
        descripcion C(500),
        activo L DEFAULT .T.
    )

    CREATE TABLE dias_descanso (
        id I PRIMARY KEY AUTOINCREMENT,
        calendario_id I,
        dia_semana I
    )
    CREATE INDEX dd_cal ON dias_descanso TAG dd_cal FOR calendario_id COMPACT

    CREATE TABLE dias_festivos (
        id I PRIMARY KEY AUTOINCREMENT,
        calendario_id I,
        fecha D,
        nombre C(150)
    )
    CREATE INDEX df_cal ON dias_festivos TAG df_cal FOR calendario_id COMPACT
    CREATE INDEX df_fecha ON dias_festivos TAG df_fecha FOR fecha COMPACT

    CREATE TABLE horarios (
        id I PRIMARY KEY AUTOINCREMENT,
        codigo C(50) UNIQUE,
        nombre C(150),
        hora_entrada T,
        hora_salida T,
        cruza_medianoche L DEFAULT .F.,
        periodo_comida_minutos I DEFAULT 30,
        dias_laborables C(200),
        tolerancia_minutos I DEFAULT 10,
        activo L DEFAULT .T.
    )
    CREATE TAG hor_codigo ON horarios TAG hor_codigo FOR UPPER(codigo) COMPACT
    CREATE INDEX hor_activo ON horarios TAG hor_activo FOR activo COMPACT

    *** Seguridad ***
    CREATE TABLE permisos (
        id I PRIMARY KEY AUTOINCREMENT,
        clave C(100) UNIQUE,
        descripcion C(500),
        modulo C(100),
        activo L DEFAULT .T.
    )
    CREATE TAG perm_clave ON permisos TAG perm_clave FOR UPPER(clave) COMPACT

    CREATE TABLE roles (
        id I PRIMARY KEY AUTOINCREMENT,
        nombre C(100) UNIQUE,
        descripcion C(500),
        activo L DEFAULT .T.
    )
    CREATE TAG rol_nombre ON roles TAG rol_nombre FOR UPPER(nombre) COMPACT

    CREATE TABLE usuarios (
        id I PRIMARY KEY AUTOINCREMENT,
        username C(100) UNIQUE,
        nombre_completo C(200),
        email C(200),
        password_hash C(255),
        activo L DEFAULT .T.,
        ultimo_acceso T,
        bloqueado_hasta T,
        intentos_fallidos I DEFAULT 0,
        debe_cambiar_password L DEFAULT .F.
    )
    CREATE TAG usu_username ON usuarios TAG usu_username FOR UPPER(username) COMPACT
    CREATE TAG usu_email ON usuarios TAG usu_email FOR UPPER(email) COMPACT

    CREATE TABLE usuario_rol (
        id I PRIMARY KEY AUTOINCREMENT,
        usuario_id I,
        rol_id I
    )
    CREATE INDEX ur_usu ON usuario_rol TAG ur_usu FOR usuario_id COMPACT
    CREATE INDEX ur_rol ON usuario_rol TAG ur_rol FOR rol_id COMPACT

    CREATE TABLE rol_permiso (
        id I PRIMARY KEY AUTOINCREMENT,
        rol_id I,
        permiso_id I
    )
    CREATE INDEX rp_rol ON rol_permiso TAG rp_rol FOR rol_id COMPACT
    CREATE INDEX rp_perm ON rol_permiso TAG rp_perm FOR permiso_id COMPACT

    CREATE TABLE sesiones (
        id I PRIMARY KEY AUTOINCREMENT,
        usuario_id I,
        token_jti C(255),
        fecha_expiracion T,
        fecha_revocacion T,
        direccion_ip C(45),
        agente_usuario C(500)
    )
    CREATE INDEX ses_usu ON sesiones TAG ses_usu FOR usuario_id COMPACT
    CREATE INDEX ses_jti ON sesiones TAG ses_jti FOR token_jti COMPACT

    CREATE TABLE auditoria (
        id I PRIMARY KEY AUTOINCREMENT,
        usuario_id I,
        fecha_hora T,
        operacion C(50),
        entidad C(100),
        registro_id C(255),
        valor_anterior M,
        valor_nuevo M,
        motivo C(500),
        resultado C(20) DEFAULT "exito",
        direccion_ip C(45),
        detalles M
    )
    CREATE INDEX aud_ent ON auditoria TAG aud_ent FOR entidad COMPACT
    CREATE INDEX aud_fecha ON auditoria TAG aud_fecha FOR fecha_hora COMPACT
    CREATE INDEX aud_usu ON auditoria TAG aud_usu FOR usuario_id COMPACT

    CREATE TABLE archivos_adjuntos (
        id I PRIMARY KEY AUTOINCREMENT,
        nombre_archivo C(255),
        ruta_almacenamiento C(500),
        mime_type C(100),
        tamano_bytes I,
        fecha_subida T,
        usuario_subida_id I,
        acceso_restringido L DEFAULT .F.
    )

    *** Empleados y nómina ***
    CREATE TABLE empleados (
        id I PRIMARY KEY AUTOINCREMENT,
        numero_empleado C(50) UNIQUE,
        nombre C(100),
        apellido_paterno C(100),
        apellido_materno C(100),
        departamento_id I,
        puesto_id I,
        fecha_ingreso D,
        estado C(50) DEFAULT "activo"
    )
    CREATE TAG emp_numero ON empleados TAG emp_numero FOR UPPER(numero_empleado) COMPACT
    CREATE INDEX emp_depto ON empleados TAG emp_depto FOR departamento_id COMPACT
    CREATE INDEX emp_estado ON empleados TAG emp_estado FOR estado COMPACT
    CREATE INDEX emp_puesto ON empleados TAG emp_puesto FOR puesto_id COMPACT

    CREATE TABLE configuracion_salarial (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        sueldo_base N(12,2),
        periodicidad C(50),
        fecha_vigencia D,
        fecha_fin_vigencia D,
        motivo C(500)
    )
    CREATE INDEX cs_emp ON configuracion_salarial TAG cs_emp FOR empleado_id COMPACT

    CREATE TABLE asignaciones_horario (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        horario_id I,
        fecha_inicio_vigencia D,
        fecha_fin_vigencia D
    )
    CREATE INDEX ah_emp ON asignaciones_horario TAG ah_emp FOR empleado_id COMPACT
    CREATE INDEX ah_hor ON asignaciones_horario TAG ah_hor FOR horario_id COMPACT

    CREATE TABLE conceptos_nomina (
        id I PRIMARY KEY AUTOINCREMENT,
        clave C(50) UNIQUE,
        nombre C(150),
        tipo C(30),
        activo L DEFAULT .T.,
        requiere_validacion_legal L DEFAULT .F.,
        observaciones_legal M
    )
    CREATE TAG cnn_clave ON conceptos_nomina TAG cnn_clave FOR UPPER(clave) COMPACT

    *** Asistencia ***
    CREATE TABLE dispositivos_registro (
        id I PRIMARY KEY AUTOINCREMENT,
        nombre C(150),
        tipo C(50),
        identificador_externo C(200),
        ubicacion C(200),
        activo L DEFAULT .T.
    )
    CREATE INDEX dis_act ON dispositivos_registro TAG dis_act FOR activo COMPACT

    CREATE TABLE eventos_asistencia (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        dispositivo_id I,
        tipo_evento C(50),
        fecha_hora T,
        metodo_registro C(50),
        resultado_validacion C(30),
        incidencia_detectada L DEFAULT .F.,
        observaciones M,
        usuario_registro_id I
    )
    CREATE INDEX ea_emp ON eventos_asistencia TAG ea_emp FOR empleado_id COMPACT
    CREATE INDEX ea_fecha ON eventos_asistencia TAG ea_fecha FOR fecha_hora COMPACT
    CREATE INDEX ea_tipo ON eventos_asistencia TAG ea_tipo FOR tipo_evento COMPACT
    CREATE INDEX ea_val ON eventos_asistencia TAG ea_val FOR resultado_validacion COMPACT

    CREATE TABLE ajustes_asistencia (
        id I PRIMARY KEY AUTOINCREMENT,
        evento_asistencia_id I,
        valor_anterior M,
        valor_corregido M,
        motivo C(500),
        fecha_ajuste T,
        usuario_responsable_id I,
        aprobado_por_id I,
        fecha_aprobacion T
    )
    CREATE INDEX aj_evt ON ajustes_asistencia TAG aj_evt FOR evento_asistencia_id COMPACT

    CREATE TABLE incidencias (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        evento_asistencia_id I,
        fecha D,
        tipo_incidencia C(50),
        minutos_retardo I DEFAULT 0,
        tiempo_incidencia_minutos I DEFAULT 0,
        regla_aplicada C(255),
        justificada L DEFAULT .F.,
        justificante_id I,
        estado C(30) DEFAULT "pendiente",
        usuario_responsable_id I,
        fecha_modificacion T
    )
    CREATE INDEX inc_emp ON incidencias TAG inc_emp FOR empleado_id COMPACT
    CREATE INDEX inc_fecha ON incidencias TAG inc_fecha FOR fecha COMPACT
    CREATE INDEX inc_tipo ON incidencias TAG inc_tipo FOR tipo_incidencia COMPACT
    CREATE INDEX inc_est ON incidencias TAG inc_est FOR estado COMPACT

    *** Justificantes ***
    CREATE TABLE justificantes (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        tipo C(50),
        fecha_incidencia D,
        descripcion M,
        estado C(30) DEFAULT "pendiente",
        motivo_rechazo M,
        fecha_solicitud T,
        fecha_decision T,
        usuario_decision_id I,
        documento_adjunto_id I
    )
    CREATE INDEX jus_emp ON justificantes TAG jus_emp FOR empleado_id COMPACT
    CREATE INDEX jus_est ON justificantes TAG jus_est FOR estado COMPACT
    CREATE INDEX jus_fecha ON justificantes TAG jus_fecha FOR fecha_incidencia COMPACT

    *** Nómina ***
    CREATE TABLE periodos_nomina (
        id I PRIMARY KEY AUTOINCREMENT,
        nombre C(150),
        fecha_inicio D,
        fecha_fin D,
        estado C(30) DEFAULT "abierto",
        fecha_cierre T,
        usuario_cierre_id I,
        observaciones M
    )
    CREATE INDEX pn_est ON periodos_nomina TAG pn_est FOR estado COMPACT
    CREATE INDEX pn_fin ON periodos_nomina TAG pn_fin FOR fecha_fin COMPACT

    CREATE TABLE resultados_nomina (
        id I PRIMARY KEY AUTOINCREMENT,
        periodo_nomina_id I,
        empleado_id I,
        sueldo_base_periodo N(12,2),
        dias_laborables I DEFAULT 0,
        dias_asistidos I DEFAULT 0,
        faltas_registradas I DEFAULT 0,
        faltas_justificadas I DEFAULT 0,
        retardos I DEFAULT 0,
        minutos_retardo_acumulados I DEFAULT 0,
        ajustes_propuestos N(12,2) DEFAULT 0,
        ajustes_aprobados N(12,2) DEFAULT 0,
        total_percepciones N(12,2),
        total_preliminar N(12,2),
        estado_aprobacion C(30) DEFAULT "pendiente",
        fecha_calculo T
    )
    CREATE INDEX rn_per ON resultados_nomina TAG rn_per FOR periodo_nomina_id COMPACT
    CREATE INDEX rn_emp ON resultados_nomina TAG rn_emp FOR empleado_id COMPACT

    CREATE TABLE propuestas_ajuste (
        id I PRIMARY KEY AUTOINCREMENT,
        periodo_nomina_id I,
        empleado_id I,
        concepto_id I,
        importe N(12,2),
        motivo M,
        estado C(30) DEFAULT "propuesto",
        usuario_propuesta_id I,
        fecha_propuesta T,
        usuario_aprobacion_id I,
        fecha_aprobacion T
    )
    CREATE INDEX pa_per ON propuestas_ajuste TAG pa_per FOR periodo_nomina_id COMPACT
    CREATE INDEX pa_emp ON propuestas_ajuste TAG pa_emp FOR empleado_id COMPACT
    CREATE INDEX pa_est ON propuestas_ajuste TAG pa_est FOR estado COMPACT

    *** Notificaciones ***
    CREATE TABLE notificaciones (
        id I PRIMARY KEY AUTOINCREMENT,
        empleado_id I,
        departamento_id I,
        fecha D,
        tipo_incidencia C(50),
        tiempo_detectado_minutos I,
        estado_atencion C(30) DEFAULT "pendiente",
        usuario_responsable_id I,
        fecha_resolucion T,
        resolucion M
    )
    CREATE INDEX not_emp ON notificaciones TAG not_emp FOR empleado_id COMPACT
    CREATE INDEX not_fecha ON notificaciones TAG not_fecha FOR fecha COMPACT

RETURN

PROCEDURE POBLAR_DATOS_BASE
    * Inserta datos semilla iniciales (roles, permisos, configuración).
    * Equivalente a _crear_roles_y_permisos_iniciales() del proyecto Python.
    LOCAL cAdminRol

    *** Permisos base ***
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("usuarios.leer", "Leer usuarios", "Usuarios", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("usuarios.escribir", "Crear/editar usuarios", "Usuarios", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("usuarios.eliminar", "Eliminar usuarios", "Usuarios", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("empleados.leer", "Leer empleados", "Empleados", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("empleados.escribir", "Crear/editar empleados", "Empleados", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("asistencia.registrar", "Registrar eventos de asistencia", "Asistencia", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("asistencia.ajustar", "Corregir eventos de asistencia", "Asistencia", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("incidencias.leer", "Leer incidencias", "Incidencias", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("incidencias.gestionar", "Gestionar incidencias", "Incidencias", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("justificantes.leer", "Leer justificantes", "Justificantes", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("justificantes.aprobar", "Aprobar/rechazar justificantes", "Justificantes", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("nomina.leer", "Leer prenómina", "Nómina", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("nomina.calcular", "Calcular prenómina", "Nómina", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("nomina.cerrar", "Cerrar periodos de nómina", "Nómina", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("reportes.leer", "Generar reportes", "Reportes", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("auditoria.leer", "Leer auditoría", "Auditoría", .T.)
    INSERT INTO permisos (clave, descripcion, modulo, activo) VALUES ;
        ("configuracion.escribir", "Modificar configuración del sistema", "Configuración", .T.)

    *** Roles base ***
    INSERT INTO roles (nombre, descripcion, activo) VALUES ;
        ("Administrador del sistema", "Acceso total al sistema", .T.)
    INSERT INTO roles (nombre, descripcion, activo) VALUES ;
        ("Recursos Humanos", "Gestión de empleados, incidencias y justificantes", .T.)
    INSERT INTO roles (nombre, descripcion, activo) VALUES ;
        ("Responsable de nómina", "Cálculo y cierre de periodos de nómina", .T.)
    INSERT INTO roles (nombre, descripcion, activo) VALUES ;
        ("Operador de asistencia", "Registro de eventos de asistencia", .T.)
    INSERT INTO roles (nombre, descripcion, activo) VALUES ;
        ("Auditor de solo lectura", "Consulta de reportes y auditoría", .T.)

    *** Rol Administrador (id=1) obtiene todos los permisos ***
    SELECT id INTO cAdminRol FROM roles WHERE nombre = "Administrador del sistema"
    INSERT INTO rol_permiso (rol_id, permiso_id)
        SELECT cAdminRol, id FROM permisos

    *** Configuración general inicial ***
    INSERT INTO configuracion (clave, valor, descripcion, fecha_creacion) VALUES ;
        ("login_max_intentos", "5", "Máximo de intentos fallidos antes de bloquear", DATETIME())
    INSERT INTO configuracion (clave, valor, descripcion, fecha_creacion) VALUES ;
        ("login_bloqueo_minutos", "15", "Minutos de bloqueo tras exceder intentos", DATETIME())
    INSERT INTO configuracion (clave, valor, descripcion, fecha_creacion) VALUES ;
        ("access_token_expire_minutes", "30", "Tiempo de expiración de sesión (minutos)", DATETIME())
    INSERT INTO configuracion (clave, valor, descripcion, fecha_creacion) VALUES ;
        ("tolerancia_retardo_minutos", "10", "Tolerancia por defecto para retardos (minutos)", DATETIME())

RETURN

PROCEDURE ABRIR_TABLAS_SISTEMA
    * Abre todas las tablas del sistema en áreas de trabajo separadas.
    * En VFP cada tabla se abre en su propio número de área (SELECT n).
    SELECT 1; USE configuracion IN 0 ORDER cfg_clave
    SELECT 2; USE departamentos IN 0 ORDER dep_codigo
    SELECT 3; USE puestos IN 0 ORDER pue_codigo
    SELECT 4; USE calendarios_laborales IN 0
    SELECT 5; USE dias_descanso IN 0
    SELECT 6; USE dias_festivos IN 0
    SELECT 7; USE horarios IN 0 ORDER hor_codigo
    SELECT 8; USE permisos IN 0 ORDER perm_clave
    SELECT 9; USE roles IN 0 ORDER rol_nombre
    SELECT 10; USE usuarios IN 0 ORDER usu_username
    SELECT 11; USE usuario_rol IN 0
    SELECT 12; USE rol_permiso IN 0
    SELECT 13; USE sesiones IN 0
    SELECT 14; USE auditoria IN 0
    SELECT 15; USE archivos_adjuntos IN 0
    SELECT 16; USE empleados IN 0 ORDER emp_numero
    SELECT 17; USE configuracion_salarial IN 0
    SELECT 18; USE asignaciones_horario IN 0
    SELECT 19; USE conceptos_nomina IN 0 ORDER cnn_clave
    SELECT 20; USE dispositivos_registro IN 0
    SELECT 21; USE eventos_asistencia IN 0 ORDER ea_fecha
    SELECT 22; USE ajustes_asistencia IN 0
    SELECT 23; USE incidencias IN 0 ORDER inc_fecha
    SELECT 24; USE justificantes IN 0 ORDER jus_fecha
    SELECT 25; USE periodos_nomina IN 0 ORDER pn_fin
    SELECT 26; USE resultados_nomina IN 0
    SELECT 27; USE propuestas_ajuste IN 0
    SELECT 28; USE notificaciones IN 0
RETURN

PROCEDURE VERIFICAR_PRIMER_ADMIN
    * Si no existe ningún usuario, obliga a crear el primer administrador.
    * Equivalente al endpoint POST /api/v1/auth/first-admin del Python.
    LOCAL nCount
    SELECT 10
    nCount = RECCOUNT("usuarios")
    IF nCount = 0
        MESSAGEBOX("No existe ningún usuario en el sistema." + CHR(13) + ;
                   "Debe crear el primer administrador.", 64, "Hamelín RH")
        DO CREAR_PRIMER_ADMIN
    ENDIF
RETURN

PROCEDURE CREAR_PRIMER_ADMIN
    * Crea de forma segura el primer usuario administrador.
    LOCAL cUser, cPass, cNom, cEmail
    cUser = INPUTBOX("Nombre de usuario para el primer administrador:", "Primer Administrador")
    IF EMPTY(cUser)
        RETURN
    ENDIF
    cPass = INPUTBOX("Contraseña:", "Primer Administrador", "", 2)
    IF EMPTY(cPass)
        RETURN
    ENDIF
    cNom  = INPUTBOX("Nombre completo:", "Primer Administrador")
    cEmail= INPUTBOX("Correo electrónico (opcional):", "Primer Administrador")

    INSERT INTO usuarios (username, nombre_completo, email, password_hash, ;
                         activo, ultimo_acceso, intentos_fallidos, ;
                         debe_cambiar_password, fecha_creacion) VALUES ;
        (cUser, cNom, cEmail, SYS(2015), .T., DATETIME(), 0, .T., DATETIME())

    * Asignar rol de administrador (asumiendo id=1 creado en POBLAR_DATOS_BASE)
    INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (RECCOUNT("usuarios"), 1)

    DO ESCRIBIR_AUDITORIA("crear", "usuario", ALLTRIM(STR(RECCOUNT("usuarios"))), ;
        .T., "Primer administrador del sistema creado", "Creación segura del primer administrador")

    MESSAGEBOX("Primer administrador creado correctamente." + CHR(13) + ;
               "Debe cambiar la contraseña en el próximo inicio.", 64, "Hamelín RH")
RETURN

*------------------------------------------------------------------------------
* PANTALLA_LOGIN - Autenticación de usuario
*------------------------------------------------------------------------------
PROCEDURE PANTALLA_LOGIN
    * Equivalente a POST /api/v1/auth/login del Python.
    * Valida credenciales, controla bloqueo por intentos fallidos, crea sesión
    * y escribe registro de auditoría.
    LOCAL cUser, cPass, cHash, nIntentos, dBloqueo, lOk, nUserId
    LOCAL cUsuarioId, cNombre, cRol, lEsAdmin

    cUser = SPACE(100)
    cPass = SPACE(100)
    lOk   = .F.

    DO WHILE .T.
        * Formulario de login simple (READ CYCLE)
        @ 5, 10 SAY "Hamelín RH - Cool Circle" FONT "Arial", 14, BOLD
        @ 8, 10 SAY "Inicio de sesión" FONT "Arial", 12
        @ 11, 10 SAY "Usuario:" GET cUser PICTURE "!"
        @ 13, 10 SAY "Contraseña:" GET cPass PICTURE "!"
        READ CYCLE

        IF EMPTY(cUser) .OR. EMPTY(cPass)
            MESSAGEBOX("Debe ingresar usuario y contraseña.", 48, "Login")
            LOOP
        ENDIF

        * Buscar usuario por username
        SELECT 10
        LOCATE FOR UPPER(usuarios.username) = UPPER(cUser)
        IF !FOUND()
            MESSAGEBOX(MSG_LOGIN_INVALID, 16, "Login")
            LOOP
        ENDIF

        nUserId   = usuarios.id
        cHash     = usuarios.password_hash
        nIntentos = usuarios.intentos_fallidos
        dBloqueo  = usuarios.bloqueado_hasta

        * Verificar bloqueo
        IF dBloqueo > DATETIME()
            MESSAGEBOX(MSG_CUENTA_BLOQUEADA, 16, "Login")
            DO ESCRIBIR_AUDITORIA("login", "usuario", ALLTRIM(STR(nUserId)), ;
                .F., "Intento en cuenta bloqueada", "error", g_cIpEstacion)
            LOOP
        ENDIF

        * Verificar contraseña (SYS(2015) devuelve un hash simulado; en producción
        * usar una función de hash real en seguridad.prg)
        IF cHash <> SYS(2015)  && placeholder: comparar contra hash almacenado
            * Incrementar intentos fallidos
            REPLACE usuarios.intentos_fallidos WITH nIntentos + 1
            IF nIntentos + 1 >= VAL(OBTENER_CONFIG("login_max_intentos", "5"))
                dBloqueo = DATETIME() + (VAL(OBTENER_CONFIG("login_bloqueo_minutos", "15")) / 1440)
                REPLACE usuarios.bloqueado_hasta WITH dBloqueo
            ENDIF
            MESSAGEBOX(MSG_LOGIN_INVALID, 16, "Login")
            DO ESCRIBIR_AUDITORIA("login", "usuario", ALLTRIM(STR(nUserId)), ;
                .F., "Credenciales inválidas", "error", g_cIpEstacion)
            LOOP
        ENDIF

        * Autenticación exitosa
        lOk = .T.
        REPLACE usuarios.intentos_fallidos WITH 0
        REPLACE usuarios.bloqueado_hasta WITH NULL
        REPLACE usuarios.ultimo_acceso WITH DATETIME()

        cUsuarioId = ALLTRIM(STR(nUserId))
        cNombre    = usuarios.nombre_completo
        cRol       = OBTENER_ROL_USUARIO(nUserId)
        lEsAdmin   = (cRol = "Administrador del sistema")

        * Crear sesión
        g_nSesionId    = FN_CREAR_SESION(nUserId, g_cIpEstacion)
        g_cUsuarioId   = cUsuarioId
        g_cUsername    = cUser
        g_cUsuarioNom  = cNombre
        g_cRolNom      = cRol
        g_lAdmin       = lEsAdmin
        g_lSesionValida= .T.
        g_nModuloActivo= 1

        DO ESCRIBIR_AUDITORIA("login", "usuario", cUsuarioId, .T., ;
            "Inicio de sesión exitoso", "exito", g_cIpEstacion)

        MESSAGEBOX("Bienvenido, " + cNombre, 64, "Hamelín RH")
        EXIT
    ENDDO
RETURN

*------------------------------------------------------------------------------
* MENU_PRINCIPAL - Menú de navegación por módulos
*------------------------------------------------------------------------------
PROCEDURE MENU_PRINCIPAL
    * Despliega el menú principal similar al panel lateral de la app de escritorio.
    * Opciones:
    *  1 Dashboard, 2 Empleados, 3 Asistencia, 4 Incidencias, 5 Justificantes,
    *  6 Nómina, 7 Reportes, 8 Auditoría, 9 Usuarios (solo admin), 10 Cerrar sesión, 11 Salir
    DEFINE MENU principal_hamelín FROM 1,1
    PAD "Sistema" BAR 1 PROMPT "Panel de dirección"
    PAD "Sistema" BAR 2 PROMPT "Empleados"
    PAD "Sistema" BAR 3 PROMPT "Registro de asistencia"
    PAD "Sistema" BAR 4 PROMPT "Incidencias"
    PAD "Sistema" BAR 5 PROMPT "Justificantes"
    PAD "Sistema" BAR 6 PROMPT "Prenómina"
    PAD "Sistema" BAR 7 PROMPT "Reportes"
    PAD "Sistema" BAR 8 PROMPT "Auditoría"
    IF g_lAdmin
        PAD "Sistema" BAR 9 PROMPT "Usuarios y permisos"
    ENDIF
    PAD "Sesión" BAR 10 PROMPT "Cerrar sesión"
    PAD "Sesión" BAR 11 PROMPT "Salir del sistema"

    ACTIVATE MENU principal_hamelín
    g_nModuloActivo = _MENU BAR 1  && valor por defecto
RETURN

*------------------------------------------------------------------------------
* CERRAR_SESION_USUARIO - Cierre de sesión del usuario actual
*------------------------------------------------------------------------------
PROCEDURE CERRAR_SESION_USUARIO
    LOCAL nSesion
    IF g_nSesionId > 0
        SELECT 13
        LOCATE FOR sesiones.id = g_nSesionId
        IF FOUND()
            REPLACE sesiones.fecha_revocacion WITH DATETIME()
        ENDIF
    ENDIF

    DO ESCRIBIR_AUDITORIA("logout", "usuario", g_cUsuarioId, .T., "Cierre de sesión")

    g_nSesionId      = 0
    g_cUsuarioId     = ""
    g_cUsername      = ""
    g_cUsuarioNom    = ""
    g_cRolNom        = ""
    g_lAdmin         = .F.
    g_lSesionValida  = .F.
    g_nModuloActivo  = 0

    MESSAGEBOX("Sesión cerrada correctamente.", 64, "Hamelín RH")
RETURN

*------------------------------------------------------------------------------
* CIERRAR_SISTEMA - Limpieza al salir
*------------------------------------------------------------------------------
PROCEDURE CIERRAR_SISTEMA
    CLOSE DATABASE
    CLOSE ALL
    SET STATUS BAR TO
RETURN

*==============================================================================
* 8. FIN DE MAIN.PRG
*==============================================================================
