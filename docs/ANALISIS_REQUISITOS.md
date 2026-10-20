# ANALISIS DE REQUISITOS - Hamelín RH

**Producto:** Hamelín RH  
**Proveedor:** Flautista de Hamelín  
**Cliente:** Cool Circle  
**Idioma:** español de México  
**Moneda:** pesos mexicanos (MXN)  
**Versión del documento:** 1.0  
**Estado:** Borrador inicial para revisión del cliente

---

## 1. Resumen ejecutivo

Cool Circle opera con aproximadamente 85 empleados distribuidos en cinco áreas (Administración, Ventas, Almacén, Reparto y Mantenimiento). El registro de asistencia se realiza actualmente en hojas de papel y Recursos Humanos captura los datos manualmente en hojas de cálculo, lo que genera errores de captura, cálculos incorrectos de retardos y faltas, pérdida de tiempo, dificultad para consultar historiales y falta de trazabilidad.

El sistema Hamelín RH centralizará la información, automatizará los cálculos de asistencia y facilitará la preparación de reportes quincenales y una prenómina revisable. Se trata de una **aplicación de escritorio nativa** (no web) conectada a una **base de datos central (PostgreSQL)**, instalable en varias computadoras de la empresa a través de una API privada (FastAPI) cifrada.

---

## 2. Alcance funcional por módulo

| Módulo | Nombre | Función principal | Estado inicial |
|---|---|---|---|
| A | Inicio de sesión y seguridad | Autenticación, Argon2id, JWT, roles, permisos, sesiones, bloqueo, auditoría de accesos | A implementar |
| B | Usuarios, roles y permisos | Control de acceso basado en roles (RBAC), configurables por módulo y operación | A implementar |
| C | Gestión de empleados | Altas, bajas, edición, cambio de departamento, horario, sueldo con vigencia e historial, importación CSV | A implementar |
| D | Departamentos, turnos y calendarios | Catálogos de departamentos, puestos, horarios, calendarios laborales, festivos, tolerancias, turnos | A implementar |
| E | Registro de entradas y salidas | Registro rápido de entrada/salida, historial inalterable, ajustes auditable, detección de duplicados e imposibles | A implementar |
| F | Integración biométrica | Capa desacoplada para sensores de huella dactilar, simulador para demostración, registro manual de contingencia | A implementar |
| G | Motor de incidencias | Cálculo configurable de retardos, faltas, salidas anticipadas, horas extras, excepciones | A implementar |
| H | Justificantes y aprobación | Tipos médico, legal, parte de tránsito, otros; estados pendiente/en revisión/aprobada/rechazada/cancelada | A implementar |
| I | Notificaciones internas | Notificaciones a RRHH para incidencias que requieran intervención | A implementar |
| J | Control de nómina y prenómina | Prenómina revisable, periodos, cálculos paso a paso, ajustes manuales autorizados, cierre de periodos | A implementar |
| K | Reportes | 14 reportes mínimos, exportación CSV/Excel/PDF, encabezados en español | A implementar |
| L | Panel de dirección | Indicadores en tiempo real a partir de datos reales | A implementar |
| M | Auditoría | Registro de operaciones sensibles, solo lectura, protegido | A implementar |

---

## 3. Requisitos de negocio identificados

### 3.1 Horarios y sueldos iniciales (documento del cliente)

| Departamento | Entrada | Salida | Sueldo indicado | Periodicidad |
|---|---|---|---|---|
| Administración | 08:00 | 16:00 | $16,000 MXN | No especificada |
| Ventas | 09:00 | 17:00 | $12,500 MXN | No especificada |
| Almacén | 07:00 | 15:00 | $11,000 MXN | No especificada |
| Reparto | 06:30 | 14:30 | $10,000 MXN | No especificada |
| Mantenimiento | 08:30 | 16:30 | $12,000 MXN | No especificada |

**Observación crítica:** el cliente no especifica si los sueldos son mensuales, quincenales, semanales o de otra periodicidad. El sistema debe permitir configurar la periodicidad por empleado y no debe asumir un valor por defecto.

### 3.2 Reglas de cálculo iniciales

- Tolerancia inicial: 10 minutos.
- Tres retardos equivalen a una falta (regla configurable, periodo por definir).
- Tres faltas injustificadas pueden ocasionar la baja del empleado (regla sujetosa a revisión humana y legislación laboral mexicana).
- Justificantes: médicos, legales, partes de tránsito y otros configurables.
- RRHH revisa incidentes y se comunica con el trabajador para determinar justificación.
- Historial conservado.
- Reportes quincenales.
- Incidencias de lunes a sábado.
- Dispositivo de registro mediante huella dactilar (por confirmar).

### 3.3 Advertencia importante (estilo consultoría)

Estas son requisitos iniciales de un caso académico, **no una autorización para aplicar automáticamente descuentos salariales, sanciones o despidos**. Todas las reglas deben ser:
- Configurables.
- Auditables.
- Sujetas a validación humana.
- Revisadas contra las políticas y la legislación laboral aplicable en México.

---

## 4. Inconsistencias y ambigüedades detectadas

### 4.1 Inconsistencia de departamentos

- Un punto del documento menciona "cuatro departamentos".
- La lista de áreas enumera **cinco**: Administración, Ventas, Almacén, Reparto, Mantenimiento.
- **Decisión provisional:** utilizar inicialmente las cinco áreas enumeradas, sin impedir que el administrador configure departamentos adicionales.

### 4.2 Datos ambiguos o no especificados

| Dato ambiguo | Impacto | Valor provisional sugerido (demostración) |
|---|---|---|
| Periodicidad de los sueldos | Cálculo de prenómina y división de sueldo base | Configurable por empleado; valor demo: mensual, sin asumir división entre 30 días |
| Días laborales y descansos | Calendario laboral y cálculo de faltas | Lunes a sábado laborable, domingo descanso (por confirmar) |
| Periodo de comida dentro del horario | Cálculo de horas trabajadas y salidas anticipadas | No se asume; se deja como campo configurable |
| Qué eventos se registran (entrada/salida/descansos) | Modelo de eventos de asistencia | Inicialmente entrada y salida únicamente |
- Qué constituye una falta justificada | Motor de incidencias y justificantes | Pendiente de política del cliente |
| Qué política aplica a los minutos de retardo | Cálculo de descuentos o ajustes | Pendiente de validación; no se aplica descuento automático |
| Cómo se calculan los descuentos autorizados | Prenómina | Pendiente; conceptos configurables y sujetos a aprobación |
| Qué usuarios pueden aprobar incidencias | Permisos y flujos de trabajo | Pendiente; se sugiere RRHH y responsables de nómina autorizados |
| Qué dispositivo biométrico se usará | Integración F | Pendiente; capa desacoplada, simulador para demo |
| Red local cableada, Wi-Fi o ambas | Infraestructura y despliegue | Pendiente; se propone cableado Ethernet para terminales |
| Qué equipos ya posee la empresa | Presupuesto y equipamiento | Pendiente; se asume que no hay infraestructura (propuesta completa) |

**Política de trabajo:** estas dudas se documentan, se establecen valores de demostración claramente identificados y se continúa con el desarrollo. No se inventan decisiones empresariales definitivas.

---

## 5. Requisitos técnicos y arquitectónicos

### 5.1 Stack tecnológico seleccionado

| Capa | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python 3 (estándar estable) | Solicitado por el cliente, amplia ecosistema |
| Escritorio | PySide6 (Qt) | Interfaz nativa de escritorio, no requiere navegador |
| Servidor | FastAPI | API rápida, documentación automática, fácil de mantener |
| Base de datos | PostgreSQL | Base de datos central robusta, transaccional, de código abierto |
| ORM / Migraciones | SQLAlchemy + Alembic | Modelos tipados, migraciones versionadas |
| Validación | Pydantic | Validación de datos de entrada y modelos de intercambio |
| Empaquetado | PyInstaller | Ejecutables nativos para Windows y Linux |
| Pruebas | Pytest | Pruebas automatizadas estándar de Python |
| Hash de contraseñas | Argon2id | Algoritmo seguro recomendado |
| Sesiones | JWT | Tokens stateless para la API privada |

### 5.2 Principios de arquitectura

- Separación entre interfaz, lógica de negocio, acceso a datos y servicios.
- Validaciones en el servidor, nunca exclusivamente en la interfaz.
- Transacciones para operaciones que actualizan información relacionada.
- Migraciones versionadas con Alembic.
- Configuración mediante variables de entorno y archivos protegidos.
- Manejo de errores centralizado.
- Registros técnicos sin exponer contraseñas, datos biométricos ni información personal innecesaria.
- Código organizado por módulos, evitando archivos monolíticos.
- Sin credenciales incrustadas en el código fuente.
- Sin contraseñas predeterminadas permanentes.
- Los clientes se conectan exclusivamente a la API privada autorizada (no conexiones directas a PostgreSQL).

### 5.3 Seguridad

- Contraseñas con hash Argon2id.
- Permisos verificados en el servidor.
- Comunicación cifrada HTTPS/TLS donde corresponda.
- Validación de entradas y consultas parametrizadas (ORM).
- Gestión segura de sesiones y vencimiento por inactividad.
- Bloqueo temporal tras intentos fallidos.
- Acceso restringido a documentos adjuntos.
- Separación de entornos de desarrollo y producción.
- Copias de seguridad automáticas y procedimiento de restauración.
- Sin credenciales en el repositorio.

---

## 6. Modelo de datos (resumen)

Entidades principales:
- `usuarios`, `roles`, `permisos`, `usuario_rol`, `rol_permiso`
- `empleados`, `departamentos`, `puestos`, `horarios`, `asignaciones_horario`
- `calendarios_laborales`, `dias_festivos`, `dias_descanso`
- `dispositivos_registro`, `eventos_asistencia`, `ajustes_asistencia`
- `incidencias`, `justificantes`, `archivos_adjuntos`, `notificaciones`
- `periodos_nomina`, `configuracion_salarial`, `conceptos_nomina`, `propuestas_ajuste`, `aprobaciones`
- `exportaciones`, `auditoria`, `configuracion_general`

Relaciones normalizadas con claves primarias y foráneas, restricciones de integridad, índices para consultas frecuentes y eliminación lógica. Se documenta en `docs/MODELO_DATOS.md` y `docs/DIAGRAMA_ENTIDAD_RELACION.md`.

---

## 7. Flujo de trabajo principal (caso de uso prioritario)

1. Usuario inicia sesión con credenciales válidas.
2. Sistema valida permisos en el servidor.
3. Operador de asistencia registra entrada/salida de un empleado (rápido o biométrico).
4. Motor de incidencias detecta retardos, faltas u otras incidencias.
5. RRHH registra y aprueba/rechaza justificantes.
6. Se generan notificaciones internas para incidencias pendientes.
7. Al cierre de quincena, se prepara la prenómina revisable con ajustes autorizados.
8. Se genera el reporte quincenal de asistencia y se exporta a CSV/Excel/PDF.
9. Toda operación sensible queda registrada en la auditoría.

---

## 8. Criterios de aceptación (primera versión)

1. Iniciar sesión con diferentes roles.
2. Restringir correctamente los permisos.
3. Registrar y consultar empleados.
4. Configurar los cinco departamentos.
5. Configurar horarios y tolerancia.
6. Registrar entradas y salidas.
7. Detectar retardos e incidencias.
8. Registrar y aprobar justificantes.
9. Consultar historiales.
10. Generar un reporte quincenal.
11. Consultar minutos acumulados.
12. Preparar una prenómina revisable.
13. Registrar aprobaciones y ajustes.
14. Consultar la auditoría.
15. Exportar reportes.
16. Ejecutar varias computadoras cliente conectadas a una misma base de datos.
17. Instalar y ejecutar el cliente en cada sistema operativo objetivo.
18. Crear y restaurar una copia de seguridad.
19. Ejecutar las pruebas automatizadas.
20. Consultar la documentación completa.
21. Presentar la cotización y la lista de equipos.
22. Identificar con honestidad cualquier función todavía pendiente de validación.

---

## 9. Plan de implementación por fases

| Fase | Nombre | Objetivo | Entregable principal |
|---|---|---|---|
| 1 | Análisis | Requisitos, dudas, arquitectura, modelo de datos | docs/ANALISIS_REQUISITOS.md, docs/PREGUNTAS_PENDIENTES.md, docs/ARQUITECTURA.md, docs/MODELO_DATOS.md |
| 2 | Diseño | Base de datos, permisos, flujos, pantallas | docs/DIAGRAMA_ENTIDAD_RELACION.md, docs/DIAGRAMA_FLUJO_ASISTENCIA.md |
| 3 | Infraestructura base | Configuración, BD, migraciones, API, autenticación, permisos | server/, database/migrations/ |
| 4 | Aplicación de escritorio | Navegación, tema, componentes, formularios | desktop/app/ |
| 5 | Operación de RRHH | Empleados, horarios, asistencia, incidencias, justificantes | Módulos C, D, E, F, G, H |
| 6 | Prenómina y reportes | Reglas configurables, aprobaciones, reportes | Módulos J, K, L, M |
| 7 | Seguridad y pruebas | Pruebas, permisos, cálculos, corrección de defectos | tests/, docs/PLAN_PRUEBAS.md, docs/RESULTADOS_PRUEBAS.md |
| 8 | Instalación y distribución | Ejecutables, scripts, despliegue | deployment/, PyInstaller artifacts |
| 9 | Documentación comercial | Manuales, equipos, costos, cotización | docs/MANUAL_USUARIO.md, docs/COTIZACION_COMERCIAL.md, etc. |

---

## 10. Supuestos y limitaciones conocidas

1. No se cuenta con infraestructura existente confirmada; se propone infraestructura completa.
2. Los sueldos del cliente carecen de periodicidad definida; se deja como campo configurable.
3. La integración biométrica no se ha probado con un dispositivo real; se incluye un simulador identificado como tal para demostraciones.
4. No se implementan descuentos salariales automáticos ni CFDI de nómina.
5. La prenómina es revisable y no sustituye procesos oficiales de nómina sin validación.
6. No se promete funcionamiento sin conexión ni sincronización automática no implementada.

---

**Siguiente paso:** revisar este documento con el cliente y continuar con `docs/PREGUNTAS_PENDIENTES.md` y `docs/ARQUITECTURA.md`.