# RESULTADOS DE PRUEBAS - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0  
**Fecha:** 17 de octubre de 2026

---

## 1. Resumen

| Métrica | Valor |
|---|---|
| Pruebas automatizadas ejecutadas | 15 |
| Pruebas aprobadas | 15 |
| Pruebas fallidas | 0 |
| Pruebas omitidas | 0 |
| Entorno | PostgreSQL 18 (puerto 5433), Python 3.9.23, API FastAPI en puerto 8001 |

---

## 2. Pruebas automatizadas (pytest)

| # | Caso | Resultado |
|---|---|---|
| 1 | Hash y verificación de contraseña | Aprobado |
| 2 | Crear usuario y autenticar | Aprobado |
| 3 | Bloqueo tras intentos fallidos | Aprobado |
| 4 | Token JWT válido / inválido | Aprobado |
| 5 | Auditoría no expone credenciales | Aprobado |
| 6 | Crear empleado | Aprobado |
| 7 | Número de empleado duplicado | Aprobado |
| 8 | Cambiar estado de empleado | Aprobado |
| 9 | Estado inválido rechazado | Aprobado |
| 10 | Entrada dentro de tolerancia (sin incidencia) | Aprobado |
| 11 | Entrada fuera de tolerancia (retardo) | Aprobado |
| 12 | Entrada duplicada | Aprobado |
| 13 | Salida sin entrada (imposible) | Aprobado |
| 14 | Conteo de retardos en periodo | Aprobado |
| 15 | Prenómina sin descuentos automáticos + ajuste + cierre | Aprobado |

---

## 3. Prueba humo de extremo a extremo (API)

Se ejecutó un flujo completo contra la API en ejecución:

1. Creación del primer administrador (procedimiento seguro).
2. Login con credenciales válidas y segundo login sin conflicto de sesión (JTI único).
3. Perfil del usuario (`/me`).
4. Creación de departamento, horario y empleado.
5. Asignación de horario al empleado.
6. Registro de entrada con retardo (20 min, tolerancia 10) → incidencia detectada con regla aplicada documentada.
7. Listado de incidencias (retardo, 20 minutos, regla aplicada visible).
8. Creación de justificante médico y aprobación.
9. Creación de periodo de nómina y cálculo de prenómina (1 retardo, 20 minutos, sin descuento automático).
10. Consulta de resultados de prenómina.
11. Consulta de auditoría (operaciones registradas).
12. Panel de dirección (indicadores reales).
13. Reporte quincenal (1 fila, encabezados en español).
14. Cierre de sesión.

Resultado: **exitoso**.

---

## 4. Ejecutable PyInstaller (Linux)

- Construido correctamente (`dist/hamelin-rh`, 84 MB).
- Probado en modo offscreen: inicia sin errores.
- Windows: no construido en este entorno (requiere entorno Windows).

---

## 5. Limitaciones pendientes

- Integración biométrica con dispositivo real: no probada (simulador identificado).
- Ejecutable de Windows: no construido en este entorno.
- Pruebas de varios clientes simultáneos: no ejecutadas.
- Restauración de respaldo en producción: no ejecutada.

---

## 6. Conclusión

El núcleo funcional del servidor (autenticación, empleados, asistencia, motor de incidencias, justificantes, prenómina, auditoría, reportes) supera las pruebas automatizadas y la prueba humo de extremo a extremo. Las funciones pendientes están claramente identificadas en este informe y en `docs/PREGUNTAS_PENDIENTES.md`.
