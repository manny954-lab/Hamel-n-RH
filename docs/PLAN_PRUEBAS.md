# PLAN DE PRUEBAS - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

---

## 1. Objetivo

Validar que el sistema cumpla los criterios de aceptación y que los cálculos de asistencia y prenómina sean confiables.

---

## 2. Casos de prueba automatizados (servidor, pytest)

| Área | Casos |
|---|---|
| Autenticación | Hash/verificación de contraseña, login exitoso, credenciales incorrectas, bloqueo tras intentos fallidos, restablecimiento de intentos, token JWT válido/inválido, auditoría sin credenciales |
| Empleados | Crear empleado, número de empleado duplicado, cambio de estado, estado inválido |
| Asistencia | Entrada dentro de tolerancia (sin incidencia), entrada fuera de tolerancia (retardo), entrada duplicada, salida sin entrada (imposible), conteo de retardos en periodo |
| Prenómina | Cálculo sin descuentos automáticos, propuesta de ajuste, aprobación, cierre de periodo, cierre duplicado rechazado |

Total: 15 pruebas automatizadas.

---

## 3. Casos límite (edge cases) cubiertos

- Registros duplicados (misma fecha/hora/empleado).
- Salida sin entrada asociada (marcada como imposible).
- Entrada tardía dentro y fuera de tolerancia.
- Cambios de sueldo con vigencia (no recalcular periodos antiguos).
- Justificante aprobado después de una incidencia (marca la incidencia como justificada).
- Periodo ya cerrado (rechaza nuevo cierre).
- Intentos de login fallidos que bloquean la cuenta.

---

## 4. Pruebas no automatizadas (pendiente de ejecución en entorno real)

- Conexión de varios clientes a la misma base de datos simultáneamente.
- Ejecutable PyInstaller en Windows y Linux (Linux probado; Windows pendiente de entorno).
- Lector biométrico real (no probado; se incluye simulador identificado).
- Copia de seguridad y restauración en producción.

---

## 5. Criterios de aceptación (primera versión)

22 criterios definidos, desde inicio de sesión con diferentes roles hasta exportación de reportes y creación/restauración de respaldos.

---

## 6. Limitaciones conocidas

- No se afirma pruebas en equipos biométricos, instaladores de Windows ni sistemas operativos no ejecutados.
- Los precios de hardware son estimaciones preliminares, no cotizaciones verificadas.
