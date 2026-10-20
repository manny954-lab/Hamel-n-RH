# CREDENCIALES Y COMANDOS DE EJECUCIÓN - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín  
**Versión:** 1.0.0  
**Fecha:** 17 de octubre de 2026  
**Propósito:** Credenciales de acceso y comandos para ejecutar el sistema

---

## 1. CREDENCIALES DE USUARIO

El sistema incluye dos usuarios de demostración con diferentes niveles de permiso:

### Usuario 1: Administrador del Sistema

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin.coolcircle` |
| **Contraseña** | `AdminSeguro2026!` |
| **Nombre completo** | Administrador Sistema |
| **Correo electrónico** | admin@coolcircle.mx |
| **Rol** | Administrador del sistema |
| **Estado** | Activo |
| **Permisos** | Acceso completo a todos los módulos |

### Usuario 2: Recursos Humanos

| Campo | Valor |
|-------|-------|
| **Usuario** | `rrhh.coolcircle` |
| **Contraseña** | `RRHH2026!` |
| **Nombre completo** | RRHH Cool Circle |
| **Correo electrónico** | rrhh@coolcircle.mx |
| **Rol** | Recursos Humanos |
| **Estado** | Activo |
| **Permisos** | Acceso limitado (ver tabla abajo) |

---

## 2. PERMISOS POR ROL

### Administrador del Sistema (`admin.coolcircle`)

El administrador tiene acceso a TODOS los módulos y funciones:

| Módulo | Permisos |
|--------|----------|
| Inicio de sesión | ✅ Acceso completo |
| Empleados | Crear, editar, eliminar, cambiar departamento/estado |
| Departamentos | Crear, editar, listar |
| Horarios | Crear, editar, listar |
| Asistencia | Registrar entradas/salidas, ajustar eventos |
| Incidencias | Ver, gestionar (aprobar/rechazar) |
| Justificantes | Crear, aprobar, rechazar |
| Prenómina | Crear periodos, calcular, aprobar ajustes, cerrar periodos |
| Reportes | Generar y exportar |
| Auditoría | Ver historial completo |
| Usuarios | Crear, editar, desactivar |
| Consulta BD | Ejecutar consultas SQL SELECT directamente |
| Panel de dirección | Ver indicadores |

### Recursos Humanos (`rrhh.coolcircle`)

El usuario de RRHH tiene acceso limitado (no puede eliminar empleados ni acceder a funciones de administración):

| Módulo | Permisos |
|--------|----------|
| Inicio de sesión | ✅ Acceso completo |
| Empleados | Ver, crear, editar (NO puede eliminar) |
| Departamentos | Ver |
| Horarios | Ver |
| Asistencia | Registrar entradas/salidas |
| Incidencias | Ver, gestionar (aprobar/rechazar) |
| Justificantes | Crear, aprobar, rechazar |
| Prenómina | Ver periodos y resultados (NO puede crear/cerrar periodos) |
| Reportes | Ver |
| Auditoría | Ver |
| Usuarios | NO tiene acceso |
| Consulta BD | NO tiene acceso (módulo oculto) |

---

## 3. DIFERENCIAS ENTRE USUARIOS (para demostrar al cliente)

| Acción | Administrador (`admin.coolcircle`) | RRHH (`rrhh.coolcircle`) |
|--------|-----------------------------------|--------------------------|
| Ver módulo "Consulta BD" en menú lateral | ✅ Sí | ❌ No aparece |
| Ver botón "Eliminar" en tabla de empleados | ✅ Sí | ❌ No aparece |
| Acceder a módulo "Usuarios y permisos" | ✅ Sí | ❌ No aparece |
| Eliminar un empleado | ✅ Sí | ❌ No (botón oculto) |
| Cerrar periodos de nómina | ✅ Sí | ❌ No |
| Crear usuarios del sistema | ✅ Sí | ❌ No |
| Registrar asistencia | ✅ Sí | ✅ Sí |
| Aprobar justificantes | ✅ Sí | ✅ Sí |
| Ver panel de dirección | ✅ Sí | ✅ Sí |

---

## 4. COMANDOS PARA EJECUTAR EL SOFTWARE

### 4.1 Instalar el servidor (una sola vez)

```bash
# Entrar a la carpeta del proyecto
cd /home/Emmanuel/Documentos/OPENCODE

# Iniciar PostgreSQL (base de datos)
pg_ctl -D /tmp/pgdata -l /tmp/pg.log -o "-p 5433 -c listen_addresses='localhost' -c unix_socket_directories='/tmp'" start

# Crear base de datos (solo la primera vez)
psql -h localhost -p 5433 -U postgres -d postgres -c "CREATE DATABASE hamelin_rh;"

# Aplicar migraciones de base de datos
PYTHONPATH=. .venv/bin/python -m alembic -c alembic.ini upgrade head
```

### 4.2 Iniciar el servidor API (debe estar corriendo SIEMPRE durante la demo)

```bash
cd /home/Emmanuel/Documentos/OPENCODE
PYTHONPATH=server .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

**Verificar que el servidor está vivo:**
```bash
curl -s http://127.0.0.1:8001/health
# Debe responder: {"status":"ok","service":"hamelin-rh-api"}
```

### 4.3 Ejecutar el cliente de escritorio

**Opción A: Usando el ejecutable compilado (recomendado)**
```bash
cd /home/Emmanuel/Documentos/OPENCODE
./dist/hamelin-rh
```

**Opción B: Ejecutando desde código fuente**
```bash
cd /home/Emmanuel/Documentos/OPENCODE
QT_QPA_PLATFORM=offscreen .venv/bin/python desktop/app/main.py
# Si tienes pantalla gráfica normal, quita QT_QPA_PLATFORM=offscreen:
# .venv/bin/python desktop/app/main.py
```

---

## 5. COMANDOS DE PRUEBAS

### Ejecutar pruebas automatizadas del servidor
```bash
cd /home/Emmanuel/Documentos/OPENCODE
PYTHONPATH=server .venv/bin/python -m pytest server/tests -v
```
Resultado esperado: 15 pruebas aprobadas.

### Consultar la base de datos directamente
```bash
psql -h localhost -p 5433 -U postgres -d hamelin_rh
```

Ejemplos de consultas útiles:
```sql
-- Ver todos los empleados y sus sueldos
SELECT e.numero_empleado, e.nombre, e.apellido_paterno, d.nombre AS departamento, cs.sueldo_base
FROM empleados e
JOIN departamentos d ON e.departamento_id = d.id
JOIN configuracion_salarial cs ON cs.empleado_id = e.id
ORDER BY e.numero_empleado;

-- Ver usuarios del sistema
SELECT username, nombre_completo, email, activo FROM usuarios;

-- Ver incidencias detectadas
SELECT i.tipo_incidencia, i.minutos_retardo, e.numero_empleado
FROM incidencias i
JOIN empleados e ON i.empleado_id = e.id;
```

---

## 5. FLUJO DE DEMOSTRACIÓN RECOMENDADO (15 minutos)

| Minuto | Módulo | Qué mostrar |
|--------|--------|-------------|
| 0-2 | Inicio de sesión | Iniciar como `admin.coolcircle` / `AdminSeguro2026!` |
| 2-5 | Panel de dirección | Métricas en tiempo real (empleados activos, incidencias, etc.) |
| 5-8 | Empleados | Mostrar 86 empleados, crear uno nuevo, editar uno existente |
| 8-10 | Registro de asistencia | Registrar entrada con retardo, mostrar detección automática |
| 10-12 | Incidencias | Mostrar retardos detectados con regla aplicada |
| 12-14 | Justificantes | Crear justificante médico, aprobarlo |
| 14-16 | Prenómina | Calcular quincena, mostrar sueldos base y minutos de retardo |
| 16-18 | Reportes | Generar reporte quincenal |
| 18-20 | Auditoría y Consulta BD | Mostrar historial de operaciones y consultar BD directamente |

---

## 6. COMANDOS DE RESPALDO (opcional)

```bash
# Crear copia de seguridad de la base de datos
pg_dump -h localhost -p 5433 -U postgres hamelin_rh > respaldo_hamelin_rh_$(date +%F).sql

# Restaurar copia de seguridad
pg_dump -h localhost -p 5433 -U postgres hamelin_rh < respaldo_hamelin_rh_fecha.sql
```

---

## 7. LIMITACIONES CONOCIDAS (para informar al cliente)

| Limitación | Descripción |
|------------|-------------|
| Funcionamiento sin conexión | No implementado. Requiere servidor y red local activos. |
| Lector biométrico real | No probado con dispositivo físico. Incluye simulador identificado como tal. |
| Exportación a PDF | No implementada. Los reportes se ven en pantalla; exportación a CSV disponible vía navegador. |
| Ejecutable de Windows | No construido en este entorno. Requiere compilar en máquina Windows. |
| Descuentos salariales automáticos | No implementados. Requieren revisión humana y validación legal. |
| CFDI de nómina | No implementado. No sustituye procesos fiscales oficiales. |

---

## 8. CONTACTO DE SOPORTE

**Proveedor:** Flautini de Hamelín  
**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0.0  
**Documentación completa:** Carpeta `docs/` del proyecto  
**Estado de implementación:** `docs/ESTADO_PROYECTO.md`

---

**Nota:** Los usuarios y contraseñas son de demostración. Cambiar las credenciales antes de usar en producción.