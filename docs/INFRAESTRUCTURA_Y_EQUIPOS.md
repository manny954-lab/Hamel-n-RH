# INFRAESTRUCTURA Y EQUIPOS - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

---

## 1. Escenarios propuestos

Cool Circle cuenta con ~85 empleados y 5 departamentos. No se presupone infraestructura existente.

| Escenario | Descripción |
|---|---|
| A. Piloto académico / pequeña empresa | Servidor en una máquina dedicada modesta, 1-2 terminales de registro, 2-3 estaciones administrativas |
| B. Producción recomendada | Servidor dedicado, UPS, red cableada, 2 terminales de registro, 3 estaciones administrativas, respaldo externo |

No se recomienda comprar una computadora para cada empleado automáticamente. Se determinan las terminales de registro y estaciones administrativas según el flujo de trabajo.

---

## 2. Lista de equipos y componentes

| Equipo / componente | Cantidad | Mínimo | Recomendado | Función | Justificación | Precio unitario est. (MXN) | Subtotal | Prioridad |
|---|---|---|---|---|---|---|---|---|
| Servidor dedicado | 1 | 2 vCPU, 4 GB RAM, 100 GB SSD | 4 vCPU, 8 GB RAM, 240 GB SSD | Aloja API y PostgreSQL central | Fuente única de datos para todos los clientes | 15,000 | 15,000 | Alta |
| UPS | 1 | 600 VA | 1000 VA | Protección contra cortes de energía | Evita corrupción de BD y apagones | 2,500 | 2,500 | Alta |
| Switch de red | 1 | 5 puertos Gigabit | 16 puertos Gigabit | Conecta clientes y servidor | Red local cableada | 1,500 | 1,500 | Alta |
| Cableado Ethernet | 1 lote | Cat 5e | Cat 6 | Cableado estructurado | Conexión estable a terminales | 3,000 | 3,000 | Alta |
| Router / firewall | 1 | Wi-Fi básico | Firewall con reglas | Gateway y protección de red | Seguridad del tráfico local | 2,000 | 2,000 | Media |
| Terminal de registro de asistencia | 2 | PC básica, Windows/Linux | PC táctil, lector integrado | Registro rápido entrada/salida | Entrada/salida de empleados | 8,000 | 16,000 | Alta |
| Lector biométrico compatible | 2 | USB, SDK disponible | Modelo probado con evaluación | Registro por huella (opcional) | Integración desacoplada | 6,000 | 12,000 | Media |
| Estación administrativa (RRHH) | 1 | 4 GB RAM, 128 GB SSD | 8 GB RAM, 256 GB SSD | Gestión de empleados, incidencias, prenómina | Trabajo de RRHH | 10,000 | 10,000 | Alta |
| Estación administrativa (nómina) | 1 | 4 GB RAM | 8 GB RAM | Cálculo y cierre de prenómina | Trabajo de nómina | 10,000 | 10,000 | Alta |
| Estación administrativa (dirección) | 1 | 4 GB RAM | 8 GB RAM | Panel de dirección y reportes | Consultas de dirección | 10,000 | 10,000 | Media |
| Monitores y periféricos | 5 kits | Monitor 19", teclado, ratón | Monitor 22", teclado, ratón | Periféricos de estaciones | Uso diario | 2,500 | 12,500 | Alta |
| Impresora | 0 | - | Multifunción | Solo si procesos lo requieren | No es crítica para el flujo digital | 4,000 | 0 | Baja |
| Medio de respaldo externo | 1 | Disco USB 1 TB | NAS o nube cifrada | Copias de seguridad fuera del servidor | Resiliencia ante fallos | 2,000 | 2,000 | Alta |
| SO del servidor | 1 | Linux (gratis) | Linux con soporte | Sistema operativo del servidor | Estabilidad y costo | 0 | 0 | Alta |
| SO de los clientes | 5 | Windows 10 / Linux | Windows 10 / Linux | Sistemas operativos cliente | Compatibilidad con ejecutables | 0 | 0 | Alta |

**Subtotal estimado de equipos:** ~96,500 MXN (preliminar, sin IVA, sin verificar con proveedores actuales).

**Costos recurrentes:** mantenimiento de servidor, electricidad, posible licencia de soporte, actualizaciones.

---

## 3. Comparativa: servidor dedicado vs máquina administrativa

| Aspecto | Servidor dedicado | Máquina administrativa compartida |
|---|---|---|
| Rendimiento | Dedico a la API y BD | Compite con tareas de oficina |
| Disponibilidad | Mayor (puede contar con UPS) | Menor (apagado/reinicio frecuente) |
| Seguridad | Mejor aislamiento | Mayor exposición |
| Costo inicial | Mayor | Menor |
| Recomendación | Producción recomendada | Piloto académico únicamente |

---

## 4. Diagrama de red (texto)

```
[Terminales de registro] ----+
[Estaciones administrativas] ----+---- [Switch] ---- [Router/Firewall] ---- [Internet opcional]
                                 |
                        [Servidor central]
                                 |
                          [API FastAPI (puerto 8001)]
                                 |
                          [PostgreSQL (BD central)]
                                 |
                          [Respaldo externo / UPS]

Un única fuente de datos: todos los clientes consultan la misma base de datos a través de la API.
```

---

## 5. Antecedentes de fallo

- **Si se pierde la red:** los clientes no pueden registrar ni consultar hasta restablecer la conexión. No se promete funcionamiento sin conexión ni sincronización automática no implementada.
- **Si se apaga el servidor:** la API y la BD quedan inaccesibles para todos los clientes.
- **Si falla una terminal:** solo afecta a esa estación; el resto continúa operando contra el servidor central.

---

## 6. Notas de precios

Los precios son estimaciones preliminares en MXN y deben cotizarse con proveedores locales. No se presentan como precios verificados ni definitivos. Se separa el costo del software del costo de hardware, infraestructura, licencias, soporte e impuestos (ver `docs/COTIZACION_COMERCIAL.md`).
