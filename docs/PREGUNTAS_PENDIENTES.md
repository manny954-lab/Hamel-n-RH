# PREGUNTAS PENDIENTES - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín  
**Versión:** 1.0  
**Estado:** Abierto — awaiting client feedback

Este documento recopila todas las dudas, ambigüedades y decisiones pendientes detectadas durante el análisis de requisitos. **No se inventan decisiones empresariales definitivas.** Cada respuesta del cliente se registrará aquí con su fecha y se reflejará en la configuración del sistema.

---

## 1. Datos del caso del cliente (requiere confirmación)

| # | Pregunta | Área impactada | Prioridad | Respuesta del cliente (fecha) |
|---|---|---|---|---|
| P-01 | ¿Los sueldos indicados ($16,000, $12,500, $11,000, $10,000, $12,000 MXN) son mensuales, quincenales, semanales o de otra periodicidad? | Prenómina, sueldos de empleados | Alta (bloquea cálculo de prenómina) | Pendiente |
| P-02 | ¿Cuáles son los días laborales de la empresa? ¿Se trabaja sábado? ¿Descansa domingo? | Calendario laboral, cálculo de faltas | Alta | Pendiente |
| P-03 | ¿Los horarios de entrada/salida incluyen un periodo de comida? ¿Cuál es su duración? | Cálculo de horas trabajadas, salidas anticipadas | Media | Pendiente |
| P-04 | ¿Se registrarán únicamente entrada y salida, o también descansos y salidas temporales? | Modelo de eventos de asistencia | Media | Pendiente |
| P-05 | ¿Qué constituye una falta justificada? ¿Solo justificantes médicos, legales y de tránsito, o hay otros motivos? | Motor de incidencias, justificantes | Media | Pendiente |
| P-06 | ¿Qué política se aplica a los minutos de retardo acumulado? ¿Se descuenta, se acumula o solo se reporta? | Prenómina, motor de incidencias | Alta | Pendiente |
| P-07 | ¿Cómo se calculan los descuentos autorizados (fórmula, base, días del mes)? ¿Requieren validación legal? | Prenómina | Alta | Pendiente |
| P-08 | ¿Qué usuarios o roles pueden aprobar incidencias y justificantes? | Permisos, flujos de trabajo | Alta | Pendiente |
| P-09 | ¿Qué dispositivo biométrico (marca, modelo, SDK) se utilizará para el registro por huella? | Integración biométrica | Media | Pendiente |
| P-10 | ¿La empresa dispone de red local cableada, Wi-Fi o ambas? | Infraestructura, despliegue | Media | Pendiente |
| P-11 | ¿Qué equipos (servidor, terminales, computadoras cliente) posee ya la empresa? | Infraestructura, presupuesto | Media | Pendiente |
| P-12 | ¿Cuántas terminales de registro de asistencia se necesitan y en qué ubicaciones? | Infraestructura, flujo de trabajo | Media | Pendiente |
| P-13 | ¿Cuántas estaciones administrativas (RRHH, nómina, dirección) se requieren? | Infraestructura, licencias de cliente | Media | Pendiente |
| P-14 | ¿Existe una política de retención de datos definida (cuánto conservar registros de asistencia y auditoría)? | Base de datos, respaldos | Media | Pendiente |
| P-15 | ¿Se requiere consentimiento escrito de empleados para el uso de datos biométricos, de acuerdo con la ley mexicana de protección de datos? | Seguridad, privacidad, biometría | Alta | Pendiente |

---

## 2. Reglas de cálculo y negocio (requiere configuración o validación)

| # | Pregunta | Valor provisional de demostración | Área impactada |
|---|---|---|---|
| P-16 | ¿Cuántos minutos exactos definen la tolerancia? ¿El minuto 11 está dentro o fuera de la tolerancia? | 10 minutos; el minuto 11 se considera fuera de tolerancia | Motor de incidencias |
| P-17 | ¿En qué periodo se cuenta la regla "tres retardos equivalen a una falta" (mes, quincena, año)? | Quincena (por definir) | Motor de incidencias |
| P-18 | ¿Qué ocurre con los retardos que después son justificados? ¿Se eliminan del conteo? | Se marchan como justificados y no cuentan para la regla | Motor de incidencias |
| P-19 | ¿Se aplican automáticamente descuentos por retardos o faltas? | No. Solo se proponen ajustes sujetos a autorización humana | Prenómina |
| P-20 | ¿Tres faltas injustificadas provocan automáticamente la baja del empleado? | No. Es una regla de alerta sujeta a revisión humana y legislación laboral | Gestión de empleados / incidencias |
| P-21 | ¿Qué días se consideran festivos en el calendario de Cool Circle? | Ninguno por defecto; configurables | Calendarios laborales |
| P-22 | ¿Existen turnos que cruzan medianoche en algún departamento? | No en el primer escenario; soporte técnico preparado | Horarios |

---

## 3. Técnicas e infraestructura (requiere decisión de implementación)

| # | Pregunta | Opción provisional | Área impactada |
|---|---|---|---|
| P-23 | ¿Sistema operativo del servidor? | Linux (Debian/Ubuntu) recomendado; Windows posible | Despliegue |
| P-24 | ¿Sistema operativo de las computadoras cliente? | Windows 10/11 y Linux | Despliegue, PyInstaller |
| P-25 | ¿Se requiere comunicación cifrada HTTPS/TLS en red local? | Sí, recomendado en producción | Seguridad, API |
| P-26 | ¿Dónde se almacenan las copias de seguridad y con qué frecuencia? | Disco externo o destino independiente, diarias | Respaldos |
| P-27 | ¿Se permite uso del sistema sin conexión a la red? | No se promete. No implementado en esta versión | Infraestructura |
| P-28 | ¿Se requiere firma electrónica o constancia de recibo de prenómina? | No en la primera versión | Prenómina |

---

## 4. Formatos y presentación

| # | Pregunta | Valor por defecto (configurable) |
|---|---|---|
| P-29 | Formato de fecha | DD/MM/AAAA |
| P-30 | Formato de hora | 24 horas |
| P-31 | Zona horaria | America/Mexico_City |
| P-32 | Moneda | Pesos mexicanos (MXN) |
| P-33 | Idioma de interfaz | Español de México |

---

## 5. Procedimiento para responder

1. El cliente revisa cada pregunta y anota su respuesta en la columna correspondiente.
2. Flautista de Hamelín actualiza este documento con fecha y versión.
3. Las respuestas que impliquen cambios de requisito se reflejan en `docs/ANALISIS_REQUISITOS.md`.
4. Las respuestas que impliquen cambios técnicos se reflejan en `docs/ARQUITECTURA.md` o `docs/MODELO_DATOS.md`.
5. Las preguntas con valor provisional se mantienen claramente identificadas como "demostración" hasta que el cliente las valide.

---

**Nota:** el desarrollo continúa con valores de demostración claramente identificados para las preguntas sin respuesta, sin bloquear el proyecto.