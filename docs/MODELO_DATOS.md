# MODELO DE DATOS - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0  
**Estado:** Diseño para implementación

---

## 1. Principios de modelado

- Base de datos relacional normalizada (3FN).
- Claves primarias y foráneas en todas las relaciones relevantes.
- Restricciones de integridad (unique, not null, check).
- Índices para consultas frecuentes (empleado, fecha, departamento, estado).
- Fechas de creación y modificación en tablas transaccionales.
- Eliminación lógica (`activo` / `eliminado_en`) cuando sea necesario.
- Historial de cambios relevantes en tablas de auditoría y configuración con vigencia.
- Migraciones versionadas con Alembic.

---

## 2. Tablas y relaciones

### 2.1 Seguridad y acceso

**usuarios**
- id (PK, UUID)
- username (unique, not null)
- password_hash (not null)
- nombre_completo (not null)
- email (unique)
- activo (boolean, default true)
- fecha_creación (not null)
- fecha_modificación
- ultimo_acceso
- bloqueado_hasta (timestamp, nulo si no está bloqueado)
- intentos_fallidos (integer, default 0)
- debe_cambiar_password (boolean, default false)

**roles**
- id (PK, UUID)
- nombre (unique, not null) — ej. Administrador, Dirección, RRHH, Nómina, Supervisor, Operador, Auditor
- descripcion
- activo (boolean, default true)

**permisos**
- id (PK, UUID)
- clave (unique, not null) — ej. empleados.leer, asistencia.registrar, nomina.cerrar_periodo
- descripcion
- modulo (not null) — ej. empleados, asistencia, nomina, reportes

**usuario_rol** (usuario_id, rol_id, PK compuesta)

**rol_permiso** (rol_id, permiso_id, PK compuesta)

**sesiones**
- id (PK, UUID)
- usuario_id (FK -> usuarios)
- token_jti (unique)
- fecha_creación (not null)
- fecha_expiración (not null)
- fecha_revocación
- direccion_ip
- agente_usuario

**auditoria**
- id (PK, UUID)
- usuario_id (FK -> usuarios, nullable)
- fecha_hora (not null)
- operacion (not null) — ej. crear, actualizar, eliminar, aprobar, rechazar, exportar
- entidad (not null) — nombre de la tabla/entidad afectada
- registro_id (identificador del registro afectado)
- valor_anterior (JSON, nullable)
- valor_nuevo (JSON, nullable)
- motivo (nullable)
- resultado (not null) — exito / error
- direccion_ip (nullable)
- detalles (JSON, nullable)

---

### 2.2 Catálogos organizativos

**departamentos**
- id (PK, UUID)
- codigo (unique, not null)
- nombre (not null)
- activo (boolean, default true)
- fecha_creación
- usuario_creacion_id (FK -> usuarios)

**puestos**
- id (PK, UUID)
- codigo (unique, not null)
- nombre (not null)
- departamento_id (FK -> departamentos)
- activo (boolean, default true)

**horarios**
- id (PK, UUID)
- codigo (unique, not null)
- nombre (not null)
- hora_entrada (time, not null)
- hora_salida (time, not null)
- cruza_medianoche (boolean, default false)
- periodo_comida_minutos (integer, default 0)
- dias_laborables (JSON, default ["lunes","martes","miercoles","jueves","viernes","sabado"])
- tolerancia_minutos (integer, default 10)
- activo (boolean, default true)

**asignaciones_horario**
- id (PK, UUID)
- empleado_id (FK -> empleados)
- horario_id (FK -> horarios)
- fecha_inicio_vigencia (date, not null)
- fecha_fin_vigencia (date, nullable)
- usuario_asignacion_id (FK -> usuarios)

**calendarios_laborales**
- id (PK, UUID)
- nombre (not null)
- descripcion
- activo (boolean, default true)

**dias_festivos**
- id (PK, UUID)
- calendario_id (FK -> calendarios_laborales)
- fecha (date, not null)
- nombre (not null)

**dias_descanso**
- id (PK, UUID)
- calendario_id (FK -> calendarios_laborales)
- dia_semana (integer, not null, 0=domingo..6=sábado)

**configuracion_general**
- clave (PK, unique, not null)
- valor (text, not null)
- descripcion
- fecha_modificación
- usuario_modificacion_id (FK -> usuarios)

---

### 2.3 Empleados

**empleados**
- id (PK, UUID)
- numero_empleado (unique, not null)
- nombre (not null)
- apellido_paterno (not null)
- apellido_materno (nullable)
- departamento_id (FK -> departamentos)
- puesto_id (FK -> puestos)
- fecha_ingreso (date, not null)
- estado (not null) — activo, baja_voluntaria, baja_involuntaria, licencia, suspendido
- usuario_creacion_id (FK -> usuarios)
- fecha_creación (not null)
- fecha_modificación
- usuario_modificacion_id (FK -> usuarios)
- eliminado_en (nullable, eliminación lógica)

**configuracion_salarial**
- id (PK, UUID)
- empleado_id (FK -> empleados)
- sueldo_base (numeric, not null)
- periodicidad (not null) — mensual, quincenal, semanal, hora
- fecha_vigencia (date, not null)
- fecha_fin_vigencia (date, nullable)
- usuario_alta_id (FK -> usuarios)
- motivo (nullable)

---

### 2.4 Asistencia y dispositivos

**dispositivos_registro**
- id (PK, UUID)
- nombre (not null)
- tipo (not null) — software, lector_biometrico, terminal
- identificador_externo (unique, nullable) — número de serie o ID del dispositivo
- ubicacion (nullable)
- activo (boolean, default true)
- fecha_registro (not null)

**eventos_asistencia**
- id (PK, UUID)
- empleado_id (FK -> empleados, not null)
- dispositivo_id (FK -> dispositivos_registro, nullable)
- tipo_evento (not null) — entrada, salida, otro
- fecha_hora (timestamp, not null)
- metodo_registro (not null) — manual, biométrico, tarjeta, simulación
- resultado_validacion (not null) — valido, duplicado, imposible, pendiente
- incidencia_detectada (boolean, default false)
- observaciones (nullable)
- fecha_creación (not null)
- usuario_registro_id (FK -> usuarios, nullable)

**ajustes_asistencia**
- id (PK, UUID)
- evento_asistencia_id (FK -> eventos_asistencia)
- valor_anterior (nullable)
- valor_corregido (nullable)
- motivo (not null)
- fecha_ajuste (not null)
- usuario_responsable_id (FK -> usuarios)
- aprobado_por_id (FK -> usuarios, nullable)
- fecha_aprobación (nullable)

---

### 2.5 Incidencias y justificantes

**incidencias**
- id (PK, UUID)
- empleado_id (FK -> empleados, not null)
- evento_asistencia_id (FK -> eventos_asistencia, nullable)
- fecha (date, not null)
- tipo_incidencia (not null) — retardo, falta, entrada_incompleta, salida_incompleta, salida_anticipada, horas_extras
- minutos_retardo (integer, default 0)
- tiempo_incidencia_minutos (integer, default 0)
- regla_aplicada (not null) — descripcion de la regla que generó la incidencia
- justificada (boolean, default false)
- justificante_id (FK -> justificantes, nullable)
- estado (not null) — pendiente, en_revision, aprobada, rechazada
- usuario_responsable_id (FK -> usuarios, nullable)
- fecha_creación (not null)
- fecha_modificación

**justificantes**
- id (PK, UUID)
- empleado_id (FK -> empleados, not null)
- tipo (not null) — medico, legal, transito, otro
- fecha_incidencia (date, not null)
- descripcion (nullable)
- estado (not null) — pendiente, en_revision, aprobada, rechazada, cancelada
- motivo_rechazo (nullable)
- fecha_solicitud (not null)
- fecha_decision (nullable)
- usuario_decision_id (FK -> usuarios, nullable)
- documento_adjunto_id (FK -> archivos_adjuntos, nullable)

**archivos_adjuntos**
- id (PK, UUID)
- nombre_archivo (not null)
- ruta_almacenamiento (not null)
- mime_type (nullable)
- tamano_bytes (integer)
- fecha_subida (not null)
- usuario_subida_id (FK -> usuarios)
- acceso_restringido (boolean, default true)

---

### 2.6 Notificaciones

**notificaciones**
- id (PK, UUID)
- empleado_id (FK -> empleados, not null)
- departamento_id (FK -> departamentos, nullable)
- fecha (date, not null)
- tipo_incidencia (not null)
- tiempo_detectado_minutos (integer)
- estado_atencion (not null) — pendiente, revisada, resuelta
- usuario_responsable_id (FK -> usuarios, nullable)
- fecha_resolucion (nullable)
- resolucion (nullable)

---

### 2.7 Prenómina

**periodos_nomina**
- id (PK, UUID)
- nombre (not null) — ej. Quincena 1 Enero 2026
- fecha_inicio (date, not null)
- fecha_fin (date, not null)
- estado (not null) — abierto, calculado, cerrado, reabierto
- fecha_cierre (nullable)
- usuario_cierre_id (FK -> usuarios, nullable)
- observaciones (nullable)

**conceptos_nomina**
- id (PK, UUID)
- clave (unique, not null)
- nombre (not null)
- tipo (not null) — percepcion, deduccion, ajuste
- activo (boolean, default true)
- requiere_validacion_legal (boolean, default false)
- observaciones_legal (nullable)

**propuestas_ajuste**
- id (PK, UUID)
- periodo_nomina_id (FK -> periodos_nomina)
- empleado_id (FK -> empleados)
- concepto_id (FK -> conceptos_nomina)
- importe (numeric, not null)
- motivo (not null)
- estado (not null) — propuesto, aprobado, rechazado
- usuario_propuesta_id (FK -> usuarios)
- fecha_propuesta (not null)
- usuario_aprobacion_id (FK -> usuarios, nullable)
- fecha_aprobacion (nullable)

**resultados_nomina** (vista previa de prenómina por empleado y periodo)
- id (PK, UUID)
- periodo_nomina_id (FK -> periodos_nomina)
- empleado_id (FK -> empleados)
- sueldo_base_periodo (numeric)
- dias_laborables (integer)
- dias_asistidos (integer)
- faltas_registradas (integer)
- faltas_justificadas (integer)
- retardos (integer)
- minutos_retardo_acumulados (integer)
- ajustes_propuestos (numeric)
- ajustes_aprobados (numeric)
- total_percepciones (numeric)
- total_preliminar (numeric)
- estado_aprobacion (not null)
- fecha_calculo (not null)

---

## 3. Relaciones principales (resumen)

- Un usuario puede tener varios roles (usuario_rol).
- Un rol puede tener varios permisos (rol_permiso).
- Un departamento tiene varios puestos y varios empleados.
- Un empleado tiene varias asignaciones de horario (historial con vigencia).
- Un empleado tiene varias configuraciones salariales (historial con vigencia).
- Un empleado tiene varios eventos de asistencia.
- Un evento de asistencia puede generar una incidencia.
- Una incidencia puede tener un justificante.
- Un justificante puede tener un archivo adjunto.
- Un periodo de nómina tiene varios resultados de nómina y propuestas de ajuste.
- Cada operación sensible queda registrada en auditoría.

---

## 4. Índices sugeridos (implementados en migraciones)

- `eventos_asistencia(empleado_id, fecha_hora)`
- `eventos_asistencia(fecha_hora)`
- `incidencias(empleado_id, fecha)`
- `incidencias(estado)`
- `justificantes(empleado_id, estado)`
- `empleados(numero_empleado)`
- `empleados(departamento_id, estado)`
- `auditoria(fecha_hora)`
- `auditoria(usuario_id)`
- `propuestas_ajuste(periodo_nomina_id, empleado_id)`

---

## 5. Estrategia de retención y eliminación lógica

- Los empleados se desactivan (estado = baja) en lugar de borrarse, conservando su historial.
- Los eventos de asistencia no se borran; las correcciones generan ajustes con valor anterior y nuevo.
- La auditoría es de solo lectura y no se modifica ni borra.
- La retención de datos se define en `configuracion_general` y está sujeta a la política del cliente y la legislación mexicana.

---

## 6. Diagrama entidad-relación

Ver `docs/DIAGRAMA_ENTIDAD_RELACION.md`.

---