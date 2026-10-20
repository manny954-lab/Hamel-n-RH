# Hamelín RH

**Sistema de escritorio de control de asistencia, incidencias y prenómina para Cool Circle**

**Versión:** 1.0.0  
**Proveedor:** Flautista de Hamelín  
**Cliente:** Cool Circle  
**Idioma:** español de México  
**Moneda:** pesos mexicanos (MXN)  
**Estado:** Versión funcional — lista para demostración

---

## 1. Descripción del proyecto

Hamelín RH es una **aplicación de escritorio nativa** (no web, no requiere navegador) conectada a una **base de datos central PostgreSQL**. Permite a varias computadoras de la empresa trabajar con una única fuente de datos a través de una **API privada FastAPI** cifrada.

El sistema centraliza el registro de asistencia, automatiza el cálculo de incidencias (retardos, faltas, salidas incompletas, entradas incompletas), gestiona justificantes y prepara una **prenómina revisable** para Recursos Humanos.

---

## 2. Problema que resuelve

Cool Circle (~85 empleados en Administración, Ventas, Almacén, Reparto y Mantenimiento) registraba la asistencia en hojas de papel y RRHH capturaba manualmente en hojas de cálculo, generando errores de captura, cálculos incorrectos, pérdida de tiempo, dificultad para consultar historiales y falta de trazabilidad.

Hamelín RH elimina esos problemas centralizando la información y automatizando los cálculos, siempre bajo revisión humana y reglas configurables.

---

## 3. Estado actual de la implementación

###  Módulos funcionales

| Módulo | Función |
|--------|---------|
| A. Seguridad | Login, contraseñas con Argon2id, JWT, roles y permisos, bloqueo por intentos fallidos, sesiones, auditoría de accesos |
| B. Usuarios, roles y permisos | RBAC configurable por módulo y operación |
| C. Gestión de empleados | Altas, bajas, edición, historial, cambio de departamento, configuración salarial con vigencia |
| D. Catálogos | Departamentos, puestos, horarios, calendarios, festivos, tolerancias |
| E. Asistencia | Entrada/salida, detección de retardos, duplicados e imposibles |
| F. Biometría | Capa desacoplada (simulador para demostración, no es dispositivo real) |
| G. Incidencias | Motor de reglas configurable (retardo, falta, salida incompleta, entrada incompleta) |
| H. Justificantes | Médico, legal, tránsito, otro; estados y aprobación/rechazo |
| I. Notificaciones | Internas a RRHH para incidencias |
| J. Prenómina | Periodos, cálculo revisable, ajustes autorizados, cierre de periodos |
| K. Reportes | Reporte quincenal, retardos, faltas, justificantes, minutos acumulados, por empleado, etc. |
| L. Panel de dirección | Indicadores reales de la base de datos |
| M. Auditoría | Registro de operaciones sensibles, solo lectura |

### ✅ Datos cargados (demostración)

- **86 empleados** distribuidos en 5 departamentos
- **Sueldos base** (mensual, valor de demostración): $16,000 / $12,500 / $11,000 / $10,000 / $12,000 MXN
- **Horarios** configurados según el caso del cliente
- **Incidencias de ejemplo:** retardos, faltas, salidas incompletas, entradas incompletas
- **Prenómina:** periodo "Quincena 1 Enero 2026" calculada

---

## 4. Arquitectura

```
[Clientes escritorio Windows/Linux]
        |
        | HTTPS/TLS (producción) / HTTP (desarrollo)
        v
[Servidor central]
  - FastAPI (API privada, puerto 8001)
  - PostgreSQL (BD central, puerto 5433)
  - SQLAlchemy 2.0 + Alembic (migraciones)
```

- Los clientes se comunican **exclusivamente** con la API privada. No hay conexiones directas a PostgreSQL desde el cliente.
- Validaciones en el servidor, nunca exclusivamente en la interfaz.
- Transacciones para operaciones relacionadas.
- Migraciones versionadas con Alembic.

---

## 5. Tecnologías utilizadas

| Capa | Tecnología |
|------|------------|
| Lenguaje | Python 3.9+ |
| Escritorio | PySide6 (Qt) |
| Servidor API | FastAPI |
| Base de datos | PostgreSQL 14+ |
| ORM / Migraciones | SQLAlchemy 2.0 / Alembic |
| Validación | Pydantic 2.x |
| Cliente HTTP | httpx |
| Hash de contraseñas | Argon2id (vía passlib) |
| Tokens | PyJWT |
| Empaquetado | PyInstaller |
| Pruebas | pytest |

---

## 6. Estructura de carpetas

```
hamelin-rh/
├── desktop/           # Aplicación de escritorio (PySide6)
│   ├── app/
│   │   ├── api_client.py       # Cliente de API privada
│   │   ├── main.py             # Punto de entrada
│   │   ├── main_window.py      # Ventana principal con navegación
│   │   ├── ui/theme.py         # Tema oscuro profesional
│   │   ├── components/         # Componentes reutilizables
│   │   ├── models/             # Modelos Pydantic de intercambio
│   │   └── views/              # Vistas (login, dashboard, empleados, asistencia, incidencias, justificantes, nomina, reportes, auditoria, usuarios)
│   ├── hamelin-rh.spec         # Especificación PyInstaller
│   ├── requirements.txt
│   └── tests/
├── server/           # API FastAPI
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Configuración, dependencias, base de datos
│   │   ├── models/       # Modelos SQLAlchemy (28 tablas)
│   │   ├── repositories/ # Capa de acceso a datos
│   │   ├── services/     # Lógica de negocio (auth, empleados, asistencia, nomina, etc.)
│   │   └── security/     # Hash Argon2, JWT, permisos
│   ├── migrations/       # Migraciones Alembic versionadas
│   ├── requirements.txt
│   └── tests/
├── database/
├── deployment/
├── docs/               # Documentación completa (18 archivos)
├── scripts/
├── tests/
├── alembic.ini
├── .env.example
├── .gitignore
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## 7. Requisitos del sistema

### Servidor
- Sistema operativo: Linux recomendado (Debian/Ubuntu/Fedora) o Windows Server
- Python 3.9+
- PostgreSQL 14+
- 2 vCPU, 4 GB RAM mínimo (4 vCPU, 8 GB RAM recomendado)
- 100 GB SSD mínimo

### Cliente de escritorio
- Windows 10/11 o Linux
- 4 GB RAM recomendado
- Pantalla mínima 1280x720
- Acceso de red al servidor API (puerto 8001 por defecto)

---

## 8. Instalación y ejecución

### 8.1 Entorno de desarrollo

```bash
# Clonar o copiar el proyecto
cd hamelin-rh

# Crear entorno virtual (Python 3.9 recomendado)
python3.9 -m venv .venv
source .venv/bin/activate

# Instalar dependencias del servidor
pip install -r server/requirements.txt

# Instalar dependencias del escritorio
pip install -r desktop/requirements.txt
```

### 8.2 Servidor

1. Instalar PostgreSQL y crear la base de datos `hamelin_rh`.
2. Copiar `server/.env.example` a `server/.env` y ajustar `DATABASE_URL` y `SECRET_KEY`.
3. Aplicar migraciones:
   ```bash
   PYTHONPATH=. .venv/bin/python -m alembic -c alembic.ini upgrade head
   ```
4. Iniciar la API:
   ```bash
   PYTHONPATH=server .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

### 8.3 Crear el primer administrador

No existe una cuenta administrativa universal. El primero debe crearse de forma segura:

```bash
curl -X POST http://localhost:8001/api/v1/auth/first-admin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin.coolcircle","nombre_completo":"Administrador","email":"admin@coolcircle.mx","password":"ClaveSegura2026!"}'
```

### 8.4 Cliente de escritorio

**Desde el ejecutable ya compilado (Linux):**
```bash
./dist/hamelin-rh
```

**Desde código fuente:**
```bash
.venv/bin/python desktop/app/main.py
```

**Credenciales de prueba:**
- Usuario: `admin.coolcircle`
- Contraseña: `AdminSeguro2026!`

### 8.5 Generar ejecutables

```bash
# Linux
.venv/bin/python -m PyInstaller --noconfirm --clean desktop/hamelin-rh.spec

# Windows (debe ejecutarse en una máquina Windows)
pyinstaller --noconfirm --clean desktop/hamelin-rh.spec
```

---

## 9. Módulos y funcionalidades principales

### Inicio de sesión y seguridad
- Login con usuario y contraseña
- Contraseñas con hash Argon2id
- JWT con expiración
- Bloqueo temporal tras intentos fallidos
- Cierre de sesión y cambio de contraseña
- Primera administración creada de forma segura (sin credenciales predeterminadas)

### Empleados
- 86 empleados cargados en demostración
- Crear, editar, dar de baja (historial conservado)
- Cambiar departamento y puesto
- Configurar sueldo base y periodicidad con fecha de vigencia
- Detectar números de empleado duplicados

### Registro de asistencia
- Entrada y salida con fecha, hora y método de registro
- Detección de retardos (tolerancia configurable, inicialmente 10 minutos)
- Detección de duplicados, eventos imposibles y entradas sin salida

### Incidencias
- Retardo, falta, entrada incompleta, salida incompleta
- Cada incidencia muestra la regla aplicada
- Tres retardos equivalen a una falta (regla configurable)

### Justificantes
- Tipos: médico, legal, parte de tránsito, otro
- Estados: pendiente, en revisión, aprobada, rechazada, cancelada
- Solo usuarios autorizados aprueban o rechazan

### Prenómina
- Periodos de nómina (abiertos, calculados, cerrados)
- Cálculo revisable: sueldo base, días asistidos, faltas, retardos, minutos acumulados
- Ajustes propuestos y aprobados con motivo
- **No aplica descuentos automáticos** (requiere revisión humana)

### Reportes
- Reporte quincenal con todos los empleados y sus incidencias
- Encabezados en español
- Exportación a CSV (PDF y Excel en próximas versiones)

### Panel de dirección
- Indicadores reales: empleados activos, incidencias del día, pendientes, justificantes pendientes, periodos abiertos

### Auditoría
- Registro de operaciones sensibles (solo lectura para usuarios ordinarios)

---

## 10. Limitaciones conocidas

1. **Sin funcionamiento sin conexión** ni sincronización automática no implementada.
2. **Lector biométrico no probado** con dispositivo físico. Se incluye un simulador identificado como tal para demostraciones.
3. **Periodicidad de sueldos** no especificada por el cliente; se dejó como campo configurable (valor demo: mensual).
4. **No aplica descuentos salariales automáticos** ni genera CFDI de nómina.
5. **Exportación a PDF** aún no implementada (los reportes se ven en pantalla; CSV disponible próximamente).
6. **Ejecutable de Windows** debe compilarse en una máquina Windows (no se genera desde Linux).
7. Los precios de hardware en la cotización son **estimaciones preliminares**, no verificadas con proveedores.

---

## 11. Documentación disponible en `docs/`

| Documento | Contenido |
|-----------|-----------|
| `ANALISIS_REQUISITOS.md` | Análisis de requisitos del cliente |
| `PREGUNTAS_PENDIENTES.md` | Dudas y ambigüedades del caso |
| `ARQUITECTURA.md` | Arquitectura técnica y justificaciones |
| `MODELO_DATOS.md` | Modelo relacional de la base de datos |
| `DIAGRAMA_ENTIDAD_RELACION.md` | Diagrama ER (Mermaid) |
| `DIAGRAMA_FLUJO_ASISTENCIA.md` | Flujos de asistencia, incidencias, justificantes, prenómina |
| `MANUAL_USUARIO.md` | Guía para usuarios finales |
| `MANUAL_ADMINISTRADOR.md` | Guía para administradores del sistema |
| `INSTALACION_SERVIDOR.md` | Instalación del servidor paso a paso |
| `INSTALACION_WINDOWS.md` | Instalación del cliente en Windows |
| `INSTALACION_LINUX.md` | Instalación del cliente en Linux |
| `SEGURIDAD_Y_PRIVACIDAD.md` | Política de seguridad y protección de datos |
| `RESPALDO_Y_RESTAURACION.md` | Procedimiento de respaldos y restauración |
| `PLAN_PRUEBAS.md` | Plan de pruebas automatizadas |
| `RESULTADOS_PRUEBAS.md` | Resultados de las 15 pruebas ejecutadas |
| `INFRAESTRUCTURA_Y_EQUIPOS.md` | Propuesta de equipos y costos |
| `COTIZACION_COMERCIAL.md` | Cotización con 2 escenarios (software vs todo incluido) |
| `ESTADO_PROYECTO.md` | Estado actual, tareas completadas y pendientes |

---

## 12. Pruebas automatizadas

Ejecutar:
```bash
PYTHONPATH=server .venv/bin/python -m pytest server/tests -v
```

**Resultado:** 15 pruebas aprobadas (autenticación, empleados, asistencia, prenómina).

---

## 13. Seguridad

- Contraseñas con hash Argon2id, nunca en texto plano
- Permisos verificados en el servidor por cada operación sensible
- Comunicación cifrada (HTTPS/TLS en producción)
- Consultas parametrizadas mediante ORM (protección contra inyección SQL)
- Sesiones con vencimiento y bloqueo tras intentos fallidos
- Logs sin contraseñas ni datos sensibles
- Sin credenciales en el reposiento (`.env.example` solo con valores ficticios)
- Auditoría de solo lectura, protegida frente a modificaciones

---

## 14. Soporte y contacto

**Proveedor:** Flautista de Hamelín  
**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Documentación:** Carpeta `docs/`  
**Estado de implementación:** `docs/ESTADO_PROYECTO.md`

---

## 15. Licencia

Ver archivo `LICENSE`.

---

**Nota:** Este software es una solución de escritorio para control de asistencia y prenómina revisable. No sustituye procesos oficiales de nómina ni genera CFDI sin validación adicional. Todas las reglas de cálculo deben ser revisadas por Recursos Humanos y válidadas contra la legislación laboral aplicable en México antes de aplicarse a pagos reales.
