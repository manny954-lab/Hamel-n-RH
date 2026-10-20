# COTIZACIÓN COMERCIAL - Hamelín RH

**Proveedor:** Flautista de Hamelín  
**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0  
**Moneda:** pesos mexicanos (MXN)  
**IVA:** 16 % (cuando corresponda)  
**Vigencia:** 30 días calendario a partir de la fecha de emisión

---

## 1. Descripción de la solución

Hamelín RH es un sistema de escritorio instalable y ejecutable (no web, no requiere navegador) conectado a una base de datos central PostgreSQL, diseñado para centralizar el control de asistencia, automatizar el cálculo de incidencias y preparar una prenómina revisable para Cool Circle (~85 empleados, 5 departamentos). Incluye módulos de seguridad, empleados, catálogos, registro de asistencia, integración biométrica desacoplada, motor de incidencias, justificantes, notificaciones internas, prenómina, reportes, panel de dirección y auditoría.

Se entrega en dos escenarios según la necesidad de infraestructura del cliente:

- **Escenario A:** Solución de software únicamente (licencia, instalación en infraestructura del cliente, capacitación, mantenimiento y soporte). El cliente proporciona su propio servidor y equipos.
- **Escenario B:** Implementación empresarial completa (software + servidor central + estaciones administrativas + terminales de registro + red + UPS + respaldo + instalación física completa). Todo incluido.

---

## 2. Alcance de la licencia

Entrega de código fuente y ejecutables para uso interno de Cool Circle. Licencia de uso dentro de la organización del cliente. No incluye cesión de propiedad intelectual del núcleo del software.

---

## 3. Módulos incluidos (ambos escenarios)

A. Inicio de sesión y seguridad  
B. Usuarios, roles y permisos  
C. Gestión de empleados  
D. Departamentos, turnos y calendarios  
E. Registro de entradas y salidas  
F. Integración biométrica (capa desacoplada + simulador para demostración)  
G. Motor de incidencias  
H. Justificantes y aprobación  
I. Notificaciones internas  
J. Control de nómina y prenómina (revisable, no CFDI)  
K. Reportes (14 reportes, exportación CSV/Excel/PDF)  
L. Panel de dirección  
M. Auditoría

---

## 4. Entregables (ambos escenarios)

- Aplicación de escritorio para Windows y Linux (ejecutables PyInstaller)
- Servidor API FastAPI + PostgreSQL (scripts de instalación y migraciones)
- Documentación completa en español (manuales, arquitectura, seguridad, respaldo)
- Código fuente del servidor y del cliente
- Capacitación inicial (según escenario)
- Soporte y mantenimiento (según escenario)

---

## 5. Escenarios y costos

### ESCENARIO A — Software, mantenimiento y soporte (sin hardware)

**Descripción:** Entrega del software Hamelín RH para instalarse en la infraestructura que Cool Circle ya posea o adquiera por su cuenta. No incluye servidores, computadoras, terminales, cableado, lectores biométricos ni ningún equipo físico.

| Concepto | Costo estimado (MXN) |
|---|---|
| Desarrollo de software (licencia y código fuente) | 250,000 |
| Instalación y configuración en servidor del cliente | 25,000 |
| Capacitación de usuarios y administradores | 20,000 |
| Mantenimiento (12 meses) | 50,000 |
| Soporte técnico (12 meses) | 35,000 |
| Costo de equipos | 0 (proporcionados por el cliente) |
| Lectores biométricos | 0 (opcional, no incluidos) |
| Licencias externas | 0 (ninguna identificada) |
| **Subtotal** | **380,000** |
| IVA (16 %) | 60,800 |
| **Total estimado (Escenario A)** | **440,800** |

---

### ESCENARIO B — Implementación empresarial completa (todo incluido)

**Descripción:** Entrega del software Hamelín RH más todo el entorno físico necesario para operarlo: servidor central, estaciones administrativas, terminales de registro, red, cableado, UPS, medio de respaldo e instalación completa. Incluye opción de lectores biométricos.

| Concepto | Costo estimado (MXN) |
|---|---|
| Desarrollo de software (licencia y código fuente) | 250,000 |
| Instalación y configuración (servidor, red, clientes) | 45,000 |
| Capacitación de usuarios y administradores | 35,000 |
| Mantenimiento (12 meses) | 65,000 |
| Soporte técnico prioritario (12 meses) | 50,000 |
| Costo de equipos (servidor, estaciones, terminales, red, UPS, respaldo) | 144,500 |
| Lectores biométricos (2 unidades, estimación, opcional) | 12,000 |
| Licencias externas | 0 (ninguna identificada) |
| **Subtotal** | **601,500** |
| IVA (16 %) | 96,240 |
| **Total estimado (Escenario B)** | **697,740** |

---

## 6. Desglose del costo de equipos (solo Escenario B)

| Categoría | Cantidad | Subtotal estimado (MXN) | Prioridad |
|---|---|---|---|
| Servidor central | 1 | $15,000 | Alta |
| Estaciones administrativas | 5 | $50,000 | Alta |
| Terminales de registro de asistencia | 7 | $56,000 | Alta |
| Red y conectividad (switch, cableado, router/firewall) | Varios | $9,000 | Alta |
| UPS (respaldo eléctrico) | 1 | $2,500 | Alta |
| Medio de respaldo externo | 1 | $2,000 | Alta |
| Periféricos y monitores (5 kits) | 5 kits | $12,500 | Alta |
| Lectores biométricos (opcional) | 2 | $12,000 | Media |
| **Total equipos (sin biometría)** | | **$144,500** | |
| **Total equipos (con biometría)** | | **$156,500** | |

**Nota:** Los precios de equipos son estimaciones preliminares en MXN y deben cotizarse con proveedores locales antes de presentar un presupuesto definitivo.

---

## 7. Costos recurrentes (ambos escenarios)

| Concepto | Escenario A | Escenario B | Notas |
|---|---|---|---|
| Mantenimiento (anual) | $50,000 | $65,000 | Actualizaciones, parches, monitoreo |
| Soporte técnico (anual) | $35,000 | $50,000 | Soporte prioritario en B |
| Soporte en sitio (opcional) | No incluido | Incluido (visitas programadas) | Solo B |
| Copias de seguridad en la nube | Opcional | Opcional | $1,000 - $3,000 mensual |

---

## 8. Tiempo de implementación estimado

| Escenario | Tiempo estimado |
|---|---|
| A. Software, mantenimiento y soporte | 4-6 semanas |
| B. Implementación empresarial completa | 8-12 semanas |

---

## 9. Garantía propuesta

- 90 días de garantía sobre el software entregado (corrección de defectos).
- No incluye garantía sobre hardware de terceros ni sobre el dispositivo biométrico (si se adquiere).

---

## 10. Condiciones de pago sugeridas

| Porcentaje | Momento |
|---|---|
| 30 % | Al inicio del proyecto |
| 40 % | Al entregar el entorno funcional (servidor + clientes) |
| 30 % | Al cierre del proyecto y aceptación del cliente |

---

## 11. Exclusiones (ambos escenarios)

- CFDI de nómina y procesos fiscales oficiales.
- Descuentos salariales automáticos sin validación legal.
- Funcionamiento sin conexión ni sincronización automática no implementada.
- Dispositivo biométrico real (no probado; requeriría evaluación de seguridad y privacidad antes de implementarse).
- Hardware, cableado y licencias de terceros en el Escenario A (cotizarse por separado).
- Capacitación presencial fuera de la localidad del proveedor (gastos de viaje no incluidos).

---

## 12. Supuestos

- El cliente dispondrá de red local y servidor para alojar la API y PostgreSQL (Escenario A).
- Los precios de hardware son estimaciones preliminares en MXN, no cotizaciones verificadas (Escenario B).
- La periodicidad de los sueldos del cliente está por definir; se deja como campo configurable en el software.
- No se incluyen costos de licencias de sistema operativo Windows para clientes en el Escenario A.

---

## 13. Riesgos

- Compatibilidad del lector biométrico no verificada (requiere prueba con dispositivo real).
- Reglas de cálculo de nómina sujetas a validación legal y políticas del cliente.
- Cambios en requisitos que amplíen el alcance y modifiquen el presupuesto.

---

## 14. Opciones de ampliación futura

- Integración biométrica con dispositivo probado (requiere evaluación de seguridad y cumplimiento legal).
- Notificaciones por correo electrónico.
- Exportación masiva y firmas electrónicas.
- CFDI de nómina (requiere desarrollo y validación fiscal por separado, cotización aparte).
- Soporte en sitio ilimitado.

---

## 15. Nota importante

Este documento es una **estimación comercial preliminar**. El precio definitivo se definirá tras confirmar el alcance, validar la compatibilidad del dispositivo biométrico (si aplica) y cotizar el hardware con proveedores actuales. Las partes separan siempre el costo del software del costo de hardware, infraestructura, licencias, soporte e impuestos.

**Firmado:**  
Flautista de Hamelín  
Para: Cool Circle  
Fecha: ________________
