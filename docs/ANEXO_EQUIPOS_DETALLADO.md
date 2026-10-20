# ANEXO DETALLADO DE EQUIPOS Y REQUISITOS - Cotización Comercial

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín  
**Versión:** 1.0  
**Moneda:** pesos mexicanos (MXN)  
**Estado:** Estimación preliminar — precios no verificados con proveedores

---

## 1. Metodología de cálculo de equipos

No se recomienda comprar una computadora para cada empleado automáticamente. La cantidad de equipos se determina por el flujo de trabajo:

- **Terminales de registro de asistencia:** ubicadas en puntos estratégicos donde los empleados marcan entrada/salida (área de acceso, almacén, reparto, etc.).
- **Estaciones administrativas:** utilizadas por RRHH, nómina, supervisores y dirección para gestionar el sistema.
- **Servidor central:** aloja la API y la base de datos PostgreSQL; es la única fuente de datos para todos los clientes.

Cool Circle tiene aproximadamente 85 empleados distribuidos en 5 departamentos. Se propone:

| Departamento | Empleados aprox. | Terminales de registro | Estaciones administrativas |
|---|---|---|---|
| Administración | 15 | 1 | 2 (RRHH + Dirección) |
| Ventas | 20 | 1 | 1 (Supervisor) |
| Almacén | 25 | 2 | 1 (Supervisor) |
| Reparto | 15 | 2 | 1 (Supervisor) |
| Mantenimiento | 10 | 1 | 0 (usa estación compartida) |
| **Total** | **85** | **7** | **5** |

---

## 2. Detalle por tipo de equipo

### 2.1 Servidor central (base de datos y API)

| Especificación | Mínima | Recomendada |
|---|---|---|
| Procesador | 2 vCPU / 2.5 GHz | 4 vCPU / 3.0 GHz+ |
| Memoria RAM | 4 GB | 8 GB |
| Almacenamiento | 100 GB SSD | 240 GB SSD |
| Sistema operativo | Linux (Ubuntu/Debian/Fedora) | Linux con soporte empresarial |
| Conectividad | Ethernet 1 Gbps | Ethernet 1 Gbps + Wi-Fi de respaldo |
| Puertos abiertos | 8001 (API), 5433 (PostgreSQL local) | 8001, 5433, 443 (HTTPS) |

**Función:** Aloja PostgreSQL y la API FastAPI. Es la única fuente de datos; todos los clientes se conectan a él.

**Cantidad:** 1 unidad  
**Precio unitario estimado:** $15,000 MXN  
**Subtotal:** $15,000 MXN  
**Prioridad:** Alta

---

### 2.2 Estaciones administrativas (RRHH, nómina, supervisores, dirección)

Estas computadoras ejecutan el cliente de escritorio Hamelín RH para gestionar empleados, incidencias, justificantes y prenómina.

| Especificación | Mínima | Recomendada |
|---|---|---|
| Procesador | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 |
| Memoria RAM | 4 GB | 8 GB |
| Almacenamiento | 128 GB SSD | 256 GB SSD |
| Pantalla | 19 pulgadas | 22 pulgadas Full HD |
| Sistema operativo | Windows 10/11 o Linux | Windows 10/11 o Linux |
| Conectividad | Ethernet o Wi-Fi | Ethernet cableado preferido |
| Periféricos | Teclado, ratón | Teclado, ratón, monitor |

**Función:** Gestión de empleados, registro manual de contingencia, aprobación de justificantes, cálculo de prenómina, reportes, auditoría.

**Cantidad:** 5 unidades  
**Precio unitario estimado:** $10,000 MXN  
**Subtotal:** $50,000 MXN  
**Prioridad:** Alta

---

### 2.3 Terminales de registro de asistencia

Ubicadas en accesos de cada departamento para que los empleados marquen entrada/salida.

| Especificación | Mínima | Recomendada |
|---|---|---|
| Procesador | Intel Celeron / AMD Athlon | Intel Core i3 / AMD Ryzen 3 |
| Memoria RAM | 2 GB | 4 GB |
| Almacenamiento | 64 GB eMMC/SSD | 128 GB SSD |
| Pantalla | Táctil 10 pulgadas | Táctil 15 pulgadas |
| Sistema operativo | Windows 10/11 o Linux | Windows 10/11 o Linux |
| Conectividad | Ethernet | Ethernet cableado (estable) |
| Montaje | Soporte de pared o pedestal | Soporte de pared o pedestal |

**Funcionamiento:** El empleado abre el módulo de registro rápido, selecciona entrada/salida y registra el evento. También puede usarse el simulador biométrico para demostraciones (no es un lector real).

**Cantidad:** 7 unidades  
**Precio unitario estimado:** $8,000 MXN  
**Subtotal:** $56,000 MXN  
**Prioridad:** Alta

---

### 2.4 Lectores biométricos compatibles (opcional, no probados)

El cliente planteó usar sensores de huella dactilar. Esta es una estimación preliminar; **no se ha probado ningún dispositivo real**.

| Especificación | Recomendada |
|---|---|
| Tipo | Sensor de huella dactilar USB |
| Compatibilidad | SDK disponible para Windows y Linux |
| Almacenamiento | Verificación local del dispositivo (no se almacenan plantillas en la BD central por defecto) |
| Certificación | Cumplir con Ley Federal de Protección de Datos Personales (México) |

**Nota importante:** Antes de comprar, se requiere evaluación de seguridad, privacidad, consentimiento y obligaciones legales. La capa de integración del software está desacoplada para permitir distintos fabricantes.

**Cantidad:** 2 unidades (estimación para piloto)  
**Precio unitario estimado:** $6,000 MXN  
**Subtotal:** $12,000 MXN  
**Prioridad:** Media (opcional)

---

### 2.5 Red y conectividad

| Equipo | Cantidad | Especificación mínima | Especificación recomendada | Función | Justificación | Precio unitario est. (MXN) | Subtotal | Prioridad |
|---|---|---|---|---|---|---|---|---|
| Switch de red | 1 | 5 puertos Gigabit | 16 puertos Gigabit | Conecta servidor, terminales y estaciones | Red local estable | $1,500 | $1,500 | Alta |
| Cableado Ethernet | 1 lote | Cat 5e | Cat 6 | Cableado estructurado | Conexión estable a terminales | $3,000 | $3,000 | Alta |
| Router / Firewall | 1 | Wi-Fi básico | Firewall con reglas de seguridad | Gateway y protección de red | Seguridad del tráfico local | $2,000 | $2,000 | Media |
| UPS (respaldo eléctrico) | 1 | 600 VA | 1000 VA | Protección contra cortes de energía | Evita corrupción de BD y apagones | $2,500 | $2,500 | Alta |

**Subtotal red y conectividad:** $9,000 MXN  
**Prioridad:** Alta (excepto firewall: media)

---

### 2.6 Periféricos y monitores

| Equipo | Cantidad | Especificación | Función | Precio unitario est. (MXN) | Subtotal | Prioridad |
|---|---|---|---|---|---|---|
| Monitores | 5 kits | 19 pulgadas (mínimo) / 22 pulgadas Full HD (recomendado) | Estaciones administrativas | $2,500 | $12,500 | Alta |
| Teclados y ratones | 5 kits | Estándar USB | Estaciones administrativas | Incluido en estación | Incluido | Alta |
| Impresora | 0 (opcional) | Multifunción | Solo si procesos lo requieren | $4,000 | $0 | Baja |

**Subtotal periféricos:** $12,500 MXN  
**Prioridad:** Alta

---

### 2.7 Medio de respaldo externo

| Equipo | Cantidad | Especificación | Función | Precio unitario est. (MXN) | Subtotal | Prioridad |
|---|---|---|---|---|---|---|
| Disco externo o NAS | 1 | 1 TB o más, cifrado | Copias de seguridad fuera del servidor | $2,000 | $2,000 | Alta |

**Subtotal respaldo:** $2,000 MXN  
**Prioridad:** Alta

---

### 2.8 Sistemas operativos y licencias de software

| Elemento | Cantidad | Especificación | Costo estimado (MXN) | Notas |
|---|---|---|---|---|
| Sistema operativo servidor | 1 | Linux (gratis, código abierto) | $0 | Ubuntu Server, Debian o similar |
| Sistema operativo clientes | 5-7 | Windows 10/11 o Linux | $0-$15,000 | Depende de licencias existentes del cliente |
| Base de datos PostgreSQL | 1 | Código abierto | $0 | Sin costo de licencia |
| Software Hamelín RH | 1 | Desarrollo de Flautista de Hamelín | Ver cotización principal | Incluye código fuente y ejecutables |

**Nota:** No hay costos de licencia externos identificados por ahora. Pendiente de verificación si se requiere software del fabricante del lector biométrico.

---

## 3. Resumen de costos de equipos (estimación preliminar)

| Categoría | Cantidad | Subtotal estimado (MXN) | Prioridad |
|---|---|---|---|
| Servidor central | 1 | $15,000 | Alta |
| Estaciones administrativas | 5 | $50,000 | Alta |
| Terminales de registro | 7 | $56,000 | Alta |
| Lectores biométricos | 2 | $12,000 | Media (opcional) |
| Red y conectividad | Varios | $9,000 | Alta |
| Periféricos y monitores | 5 kits | $12,500 | Alta |
| Medio de respaldo externo | 1 | $2,000 | Alta |
| **Total equipos (sin biometría)** | | **$144,500** | |
| **Total equipos (con biometría)** | | **$156,500** | |

**Nota:** Estos precios son estimaciones preliminares en MXN y **no están verificados con proveedores actuales**. Deben cotizarse con proveedores locales antes de presentar un presupuesto definitivo al cliente.

---

## 4. Costos recurrentes estimados

| Concepto | Frecuencia | Costo estimado (MXN) | Notas |
|---|---|---|---|
| Mantenimiento de servidor y red | Anual | $15,000 - $25,000 | Actualizaciones, monitoreo, soporte técnico |
| Soporte de software Hamelín RH | Anual | $30,000 - $60,000 | Dependiendo del escenario (ver cotización principal) |
| Electricidad y UPS | Mensual | $500 - $1,000 | Estimado |
| Copias de seguridad en la nube (opcional) | Mensual | $1,000 - $3,000 | Si se usa almacenamiento en la nube |

---

## 5. Comparativa: servidor dedicado vs máquina administrativa compartida

| Aspecto | Servidor dedicado | Máquina administrativa compartida |
|---|---|---|
| Rendimiento | Dedicado a API y BD | Compite con tareas de oficina |
| Disponibilidad | Mayor (con UPS) | Menor (apagados frecuentes) |
| Seguridad | Mejor aislamiento | Mayor exposición |
| Costo inicial | Mayor | Menor |
| Recomendación | Producción recomendada | Piloto académico únicamente |

---

## 6. Diagrama de red (texto)

```
[Terminales de registro (7)] ----+
[Estaciones administrativas (5)] ----+---- [Switch 16 puertos] ---- [Router/Firewall] ---- [Internet opcional]
                                 |
                        [Servidor central]
                                 |
                          [API FastAPI puerto 8001]
                                 |
                          [PostgreSQL puerto 5433]
                                 |
                          [Respaldo externo / UPS]

Un única fuente de datos: todos los clientes consultan la misma base de datos a través de la API.
```

---

## 7. Antecedentes de fallo

| Escenario | Qué ocurre |
|---|---|
| Se pierde la red | Los clientes no pueden registrar ni consultar hasta restablecer la conexión. No se promete funcionamiento sin conexión ni sincronización automática no implementada. |
| Se apaga el servidor | La API y la BD quedan inaccesibles para todos los clientes. |
| Falla una terminal | Solo afecta a esa estación; el resto continúa operando contra el servidor central. |

---

## 8. Pasos para adaptar a su presupuesto

1. **Revisar infraestructura existente:** ¿Ya tiene servidores, computadoras o red? Se pueden reutilizar equipos que cumplan los requisitos mínimos.
2. **Ajustar cantidades:** Si 7 terminales son demasiadas para el piloto, se puede iniciar con 3-4 y expandir después.
3. **Omitir biometría inicialmente:** Los lectores biométricos son opcionales y no probados; el sistema funciona con registro manual.
4. **Solicitar cotizaciones:** Lleve esta lista a proveedores locales de hardware para obtener precios reales en MXN.
5. **Separar costos:** El costo de software (desarrollo, licencias, soporte) va por separado del costo de hardware e infraestructura.

---

## 9. Descargo de responsabilidad

Este documento es una **estimación preliminar**. Los precios de hardware no son cotizaciones verificadas. Flautista de Hamelín no se hace responsable de variaciones de precios, disponibilidad de equipos o incompatibilidades hasta que se realice una cotización formal con proveedores actuales y se verifique la compatibilidad de los dispositivos biométricos (si se decide incluirlos).
