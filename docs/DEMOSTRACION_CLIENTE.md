# DEMOSTRACIÓN Y EVALUACIÓN PARA EL CLIENTE - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín  
**Versión:** 1.0.0  
**Fecha:** 17 de octubre de 2026  
**Objetivo:** Guía de pruebas para evaluar el funcionamiento del sistema antes de la aceptación final

---

## 1. Introducción

Este documento contiene una serie de pruebas prácticas que el equipo de Cool Circle puede ejecutar para verificar que Hamelín RH cumple con los requisitos acordados. Cada prueba incluye:

- **Objetivo:** Qué se valida
- **Pasos a seguir:** Qué hacer en el sistema
- **Resultado esperado:** Qué debería verse
- **Criterio de aceptación:** Si pasa o no la prueba

El cliente puede ejecutar estas pruebas en cualquier orden y documentar los resultados para la evaluación final.

---

## 2. Credenciales de prueba

Para acceder al sistema durante la demostración:

| Campo | Valor |
|-------|-------|
| Usuario | `admin.coolcircle` |
| Contraseña | `AdminSeguro2026!` |
| URL del servidor | `http://<servidor>:8001` |
| Ejecutable cliente | `./dist/hamelin-rh` (Linux) |

---

## 3. Pruebas de demostración

### PRUEBA 1: Inicio de sesión y seguridad

**Objetivo:** Verificar que el sistema autentica correctamente y restringe el acceso según los permisos.

**Pasos:**
1. Ejecutar `./dist/hamelin-rh`
2. Iniciar sesión con `admin.coolcircle` / `AdminSeguro2026!`
3. Intentar acceder a un módulo sin permisos (si se tiene otro usuario con rol limitado)
4. Cerrar sesión y volver a iniciar

**Resultado esperado:**
- El login permite el acceso con credenciales válidas
- Las credenciales incorrectas muestran mensaje de error
- Cada usuario solo ve los módulos para los que tiene permisos
- El cierre de sesión revoca el acceso

**Criterio de aceptación:** ✅ El sistema autentica y restringe accesos correctamente

---

### PRUEBA 2: Gestión de empleados

**Objetivo:** Verificar el alta, edición, consulta y cambio de departamento de empleados.

**Pasos:**
1. Ir al módulo **Empleados**
2. Verificar que aparecen los 86 empleados cargados
3. Buscar un empleado por número (ej. `EMP-001`)
4. Hacer clic en **Nuevo empleado** y crear uno de prueba con:
   - Número: `EMP-TEST01`
   - Nombre: `Prueba Demostración`
   - Departamento: `Administración`
   - Fecha de ingreso: `2026-01-01`
5. Editar el empleado y cambiar su nombre
6. Cambiar su departamento a `Ventas`
7. Cambiar su estado a `licencia` y luego volver a `activo`

**Resultado esperado:**
- La lista muestra todos los empleados con nombre, departamento y estado
- La búsqueda filtra correctamente
- Se puede crear un empleado sin errores
- Los cambios de nombre, departamento y estado se guardan
- No se permiten números de empleado duplicados

**Criterio de aceptación:** ✅ CRUD de empleados funciona completamente

---

### PRUEBA 3: Configuración de departamentos y horarios

**Objetivo:** Verificar que los 5 departamentos y sus horarios están configurados correctamente.

**Pasos:**
1. Ir al módulo **Catálogos** (o **Departamentos** y **Horarios**)
2. Verificar los 5 departamentos:
   - Administración (08:00 - 16:00)
   - Ventas (09:00 - 17:00)
   - Almacén (07:00 - 15:00)
   - Reparto (06:30 - 14:30)
   - Mantenimiento (08:30 - 16:30)
3. Verificar que cada departamento tiene su horario asignado
4. Verificar la tolerancia de 10 minutos configurada

**Resultado esperado:**
- Los 5 departamentos aparecen con sus nombres y códigos
- Los horarios coinciden con los especificados por el cliente
- La tolerancia es de 10 minutos

**Criterio de aceptación:** ✅ Catálogos configurados según requisitos del cliente

---

### PRUEBA 4: Registro de asistencia y detección de incidencias

**Objetivo:** Verificar que el sistema detecta retardos, faltas y eventos imposibles.

**Pasos:**
1. Ir al módulo **Registro de asistencia**
2. Registrar una entrada para un empleado a las 08:25 (horario 08:00, tolerancia 10 min)
3. Registrar una salida para el mismo empleado a las 16:00
4. Registrar una salida sin entrada previa para otro empleado
5. Ver el módulo **Incidencias**

**Resultado esperado:**
- La entrada a las 08:25 se detecta como retardo de 25 minutos
- La regla aplicada muestra: "Retardo: entrada 08:25 supera horario 08:00 + tolerancia 10 min"
- La salida sin entrada previa se marca como "imposible"
- Las incidencias aparecen en el listado con su tipo y regla aplicada

**Criterio de aceptación:** ✅ El sistema detecta retardos y eventos anómalos correctamente

---

### PRUEBA 5: Justificantes y aprobación

**Objetivo:** Verificar el flujo completo de justificantes (solicitar, aprobar, rechazar).

**Pasos:**
1. Ir al módulo **Justificantes**
2. Crear un justificante de tipo "médico" para un empleado con retardo
3. Verificar que el estado es "pendiente"
4. Aprobar el justificante (seleccionar fila → botón Aprobar)
5. Verificar que el estado cambia a "aprobada"
6. Rechazar otro justificante con motivo

**Resultado esperado:**
- Se puede crear un justificante con tipo, fecha y descripción
- El estado inicial es "pendiente"
- Al aprobar, el estado cambia a "aprobada"
- Al rechazar, se requiere un motivo y el estado cambia a "rechazada"
- El justificante aprobado marca la incidencia relacionada como justificada

**Criterio de aceptación:** ✅ Flujo de justificantes completo y funcional

---

### PRUEBA 6: Prenómina revisable

**Objetivo:** Verificar el cálculo de prenómina y la capacidad de proponer ajustes.

**Pasos:**
1. Ir al módulo **Prenómina**
2. Ver el periodo "Quincena 1 Enero 2026"
3. Hacer clic en **Calcular prenómina**
4. Ver el listado de empleados con:
   - Sueldo base del periodo
   - Días asistidos
   - Faltas registradas y justificadas
   - Retardos y minutos acumulados
   - Total preliminar
5. Proponer un ajuste para un empleado (ej. descuento por falta no justificada)
6. Aprobar o rechazar el ajuste

**Resultado esperado:**
- Se muestra el cálculo paso a paso por empleado
- El sueldo base coincide con lo configurado ($16,000 / $12,500 / $11,000 / $10,000 / $12,000)
- Los retardos y faltas se cuentan correctamente
- No se aplican descuentos automáticos (requieren aprobación humana)
- Los ajustes aprobados se reflejan en el total preliminar

**Criterio de aceptación:** ✅ Prenómina calculable, revisable y con ajustes autorizados

---

### PRUEBA 7: Reportes quincenales

**Objetivo:** Verificar la generación de reportes con datos reales.

**Pasos:**
1. Ir al módulo **Reportes**
2. Seleccionar rango de fechas (ej. 01/01/2026 a 15/01/2026)
3. Generar el reporte quincenal
4. Verificar que muestra:
   - Número de empleado
   - Nombre completo
   - Departamento
   - Fecha de incidencia
   - Tipo de incidencia
   - Minutos de retardo
   - Estado del justificante

**Resultado esperado:**
- El reporte muestra todos los empleados con incidencias en el rango
- Los encabezados están en español
- Los datos coinciden con lo registrado en asistencia e incidencias
- Se puede exportar a CSV (funcionalidad disponible)

**Criterio de aceptación:** ✅ Reportes generados con datos reales y en español

---

### PRUEBA 8: Panel de dirección

**Objetivo:** Verificar los indicadores en tiempo real.

**Pasos:**
1. Ir al módulo **Panel de dirección**
2. Verificar los indicadores:
   - Total de empleados activos
   - Incidencias del día
   - Incidencias pendientes
   - Justificantes pendientes
   - Periodos de nómina abiertos

**Resultado esperado:**
- Los indicadores muestran datos reales de la base de datos
- No hay cifras inventadas ni simuladas
- Los números coinciden con los registros del sistema

**Criterio de aceptación:** ✅ Indicadores calculados a partir de datos reales

---

### PRUEBA 9: Auditoría

**Objetivo:** Verificar que todas las operaciones sensibles quedan registradas.

**Pasos:**
1. Ir al módulo **Auditoría**
2. Verificar que aparecen registros de:
   - Inicios de sesión
   - Creación de empleados
   - Modificaciones de empleados
   - Aprobaciones de justificantes
   - Cambios de estado
3. Verificar que cada registro tiene: usuario, fecha, operación, entidad y motivo

**Resultado esperado:**
- La auditoría muestra un historial completo de operaciones
- Cada registro incluye usuario, fecha/hora, tipo de operación y motivo
- La auditoría es de solo lectura (no se puede modificar)

**Criterio de aceptación:** ✅ Auditoría completa y de solo lectura

---

## 4. Criterios de aceptación globales

El sistema se considera aceptado si cumple con lo siguiente:

| # | Criterio | Estado |
|---|----------|--------|
| 1 | Inicio de sesión con diferentes roles funciona correctamente | ☐ |
| 2 | Los permisos restringen el acceso a módulos según el rol | ☐ |
| 3 | Se pueden registrar, editar y dar de baja empleados | ☐ |
| 4 | Los 5 departamentos y horarios están configurados | ☐ |
| 5 | Se detectan retardos, faltas y eventos imposibles | ☐ |
| 6 | Se pueden crear y aprobar/rechazar justificantes | ☐ |
| 7 | La prenómina se calcula sin descuentos automáticos | ☐ |
| 8 | Los ajustes de prenómina requieren aprobación humana | ☐ |
| 9 | Se generan reportes quincenales con datos reales | ☐ |
| 10 | El panel de dirección muestra indicadores reales | ☐ |
| 11 | La auditoría registra operaciones sensibles | ☐ |
| 12 | El sistema funciona en múltiples clientes conectados a la misma BD | ☐ |
| 13 | No hay contraseñas predeterminadas ni credenciales expuestas | ☐ |
| 14 | Los nombres de empleados se muestran correctamente | ☐ |

---

## 5. Cómo ejecutar las pruebas

### Opción A: Ejecutable de Linux (ya compilado)

```bash
cd /home/Emmanuel/Documentos/OPENCODE
./dist/hamelin-rh
```

### Opción B: Desde código fuente (requiere entorno gráfico)

```bash
cd /home/Emmanuel/Documentos/OPENCODE
.venv/bin/python desktop/app/main.py
```

### Opción C: Pruebas automatizadas (servidor)

```bash
PYTHONPATH=server .venv/bin/python -m pytest server/tests -v
```

Resultado esperado: 15 pruebas aprobadas.

---

## 6. Datos de demostración cargados

El sistema viene precargado con datos para facilitar la demostración:

| Concepto | Cantidad |
|----------|----------|
| Empleados | 86 |
| Departamentos | 5 |
| Horarios | 5 |
| Periodos de nómina | 1 (Quincena 1 Enero 2026) |
| Incidencias de ejemplo | Múltiples (retardos, faltas, salidas incompletas) |
| Justificantes de ejemplo | 1 (médico, aprobado) |

### Sueldos base configurados (valor de demostración - periodicidad mensual)

| Departamento | Sueldo base |
|--------------|-------------|
| Administración | $16,000 MXN |
| Ventas | $12,500 MXN |
| Almacén | $11,000 MXN |
| Reparto | $10,000 MXN |
| Mantenimiento | $12,000 MXN |

**Nota:** La periodicidad de los sueldos está configurada como "mensual" como valor de demostración. Este campo es configurable y debe ser validado por Cool Circle según sus políticas reales.

---

## 7. Limitaciones conocidas (pendiente de validación)

| Limitación | Descripción |
|------------|-------------|
| Lector biométrico | No probado con dispositivo físico. Se incluye simulador identificado como tal. |
| Funcionamiento offline | No implementado. Requiere conexión al servidor. |
| Exportación a PDF | Pendiente de implementación (actualmente solo vista en pantalla). |
| Ejecutable Windows | Debe compilarse en entorno Windows (no generado desde Linux). |
| Descuentos automáticos | No implementados. Requieren revisión humana y validación legal. |
| CFDI de nómina | No implementado. No sustituye procesos fiscales oficiales. |

---

## 7. Firma de aceptación

Al completar las pruebas, el cliente puede firmar la aceptación:

**Cliente:** Cool Circle  
**Representante:** ___________________________  
**Fecha:** ___________________________  
**Resultado:** ☐ Aprobado ☐ Aprobado con observaciones ☐ Rechazado  

**Observaciones:**
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________

**Proveedor:** Flautista de Hamelín  
**Representante:** ___________________________  
**Fecha:** ___________________________

---

## 8. Soporte y contacto

Para dudas durante la evaluación, contactar al equipo de desarrollo de Flautista de Hamelín. Toda la documentación técnica está disponible en la carpeta `docs/` del proyecto.
