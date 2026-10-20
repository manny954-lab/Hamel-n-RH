# ARQUITECTURA TÉCNICA - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín  
**Versión:** 1.0  
**Estado:** Aprobado para implementación

---

## 1. Visión general

Hamelín RH es una **aplicación de escritorio nativa** (no web) conectada a una **base de datos central PostgreSQL**. Los clientes de escritorio se comunican con el servidor exclusivamente a través de una **API privada FastAPI** cifrada (HTTPS/TLS en producción). No existen conexiones directas de cliente a PostgreSQL.

La arquitectura sigue capas bien separadas: presentación, lógica de negocio, acceso a datos y servicios, con validaciones en el servidor y transacciones para operaciones relacionadas.

---

## 2. Diagrama de arquitectura de alto nivel (texto)

```
                           Internet / Red local
                                 |
            +--------------------+--------------------+
            |                                           |
   [Cliente escritorio Windows]              [Servidor central Linux/Windows]
   [Cliente escritorio Linux]                   +-------------+
            |                                   |  FastAPI    |
            |   PySide6 (Qt)                    |  (Python)   |
            |   - UI + tema oscuro              |   + JWT     |
            |   - API client (httpx)            |   + SQLAlchemy|
            |   - Simulador biométrico          |   + Alembic |
            |   - Registro manual               +------+------+
            |                                         |
            |   HTTPS/TLS (producción)                |
            |   HTTP (desarrollo)                     |
            v                                         v
   [Instalador PyInstaller]                    [PostgreSQL]
                                                (BD central)
                                                + Migraciones
                                                + Respaldos
```

---

## 3. Capas y responsabilidades

### 3.1 Capa de presentación (desktop/app/ui, desktop/app/views, desktop/app/components)

- Interfaz de escritorio con PySide6 (Qt).
- Tema oscuro por defecto, tema claro opcional.
- Navegación lateral por módulos, panel principal con métricas.
- Formularios con validación, mensajes en español.
- **No contiene lógica de negocio ni reglas de cálculo.** Solo envía peticiones a la API y muestra resultados.
- Capa de cliente API (`desktop/app/api_client`) basada en `httpx`, con manejo de tokens JWT y reintentos.

### 3.2 Capa de servicios y lógica de negocio (server/app/services)

- Orquesta operaciones de negocio.
- Aplica reglas de cálculo de incidencias, tolerancias, prenómina.
- Valida permisos antes de ejecutar operaciones.
- Coordina transacciones entre repositorios.
- Nunca expone contraseñas ni datos biométricos en logs.

### 3.3 Capa de acceso a datos (server/app/repositories, server/app/models)

- Modelos SQLAlchemy declarativos.
- Repositorios por entidad con consultas parametrizadas (ORM).
- Migraciones versionadas con Alembic.
- Índices y restricciones de integridad definidos en migraciones.

### 3.4 Capa de API (server/app/api)

- Endpoints REST expuestos por FastAPI.
- Autenticación JWT (Argon2id para contraseñas).
- Validación de entradas con Pydantic schemas.
- Manejo centralizado de errores.
- Endpoints protegidos por dependencias de permisos.

### 3.5 Capa de seguridad (server/app/security)

- Hash de contraseñas con Argon2id (`passlib` / `bcrypt` compatible).
- Generación y verificación de JWT.
- Gestión de sesiones y vencimiento por inactividad.
- Bloqueo temporal tras intentos fallidos.
- Cifrado de secretos mediante variables de entorno (no en código).

---

## 4. Flujo de una petición (ejemplo: registro de entrada)

1. Usuario abre el módulo "Registro de asistencia" en el cliente de escritorio.
2. Cliente valida localmente que el usuario tenga permiso `asistencia.registrar`.
3. Cliente envía `POST /api/v1/asistencia/eventos` con token JWT.
4. Servidor valida el token, permisos y datos de entrada (Pydantic).
5. Servicio de asistencia verifica empleado, horario asignado, duplicados y eventos imposibles dentro de una transacción.
6. Motor de incidencias calcula retardo/incidencia según regla de tolerancia.
7. Se persiste `evento_asistencia` y, si aplica, `incidencia` y `notificacion`.
8. Se escribe registro en `auditoria`.
9. Servidor responde con el evento creado o error detallado en español.
10. Cliente muestra mensaje de éxito o advertencia al usuario.

---

## 5. Modelo de despliegue

- **Servidor central:** una máquina dedicada (Linux recomendado) con PostgreSQL y FastAPI.
- **Clientes:** ejecutables PyInstaller en Windows y Linux, instalados en las computadoras que necesiten acceso.
- **Terminales de registro:** computadoras cliente con el módulo de registro rápido, opcionalmente con lector biométrico.
- **Un única fuente de datos:** todos los clientes consultan la misma base de datos central a través de la API.

---

## 6. Tecnologías seleccionadas y justificación

| Capa | Tecnología | Versión | Justificación |
|---|---|---|---|
| Lenguaje | Python | 3.10+ | Solicitado por el cliente, estable y con buen soporte |
| Escritorio | PySide6 | Última estable | Interfaz nativa de escritorio, multiplataforma |
| Servidor API | FastAPI | Última estable | API rápida, documentación automática, fácil de mantener |
| Base de datos | PostgreSQL | 14+ | Transaccional, robusto, código abierto, índices |
| ORM | SQLAlchemy | 2.0+ | Modelos tipados, consultas parametrizadas |
| Migraciones | Alembic | Última estable | Migraciones versionadas y reproducibles |
| Validación | Pydantic | 2.x | Validación de entrada y modelos de intercambio |
| Cliente HTTP | httpx | Última estable | Cliente HTTP asíncrono para el desktop |
| Empaquetado | PyInstaller | Última estable | Ejecutables nativos Windows/Linux |
| Pruebas | Pytest | Última estable | Pruebas automatizadas estándar |
| Hash contraseñas | Argon2id | passlib/bcrypt | Algoritmo seguro recomendado |
| Tokens | PyJWT | Última estable | Sesiones stateless para la API |

---

## 7. Seguridad

- Contraseñas con hash Argon2id, nunca en texto plano.
- JWT con expiración y renovación controlada.
- Permisos verificados en el servidor por cada operación sensible.
- Comunicación cifrada HTTPS/TLS en entornos de producción.
- Consultas parametrizadas mediante ORM (protección contra inyección SQL).
- Validación de entradas con Pydantic.
- Sesiones con vencimiento por inactividad y bloqueo temporal tras intentos fallidos.
- Logs sin contraseñas, datos biométricos ni información personal innecesaria.
- Sin credenciales incrustadas; variables de entorno y archivo `.env` protegido.
- Sin contraseñas predeterminadas permanentes; primer administrador se crea de forma segura.

---

## 8. Decisiones de diseño pendientes (configurables, no hardcodeadas)

- Reglas de tolerancia y minutos límite (configurable por administración).
- Equivalencia retardos-falta (configurable, periodo por definir).
- Fórmulas de cálculo de prenómina y descuentos (configurables y sujetos a validación legal).
- Dispositivo biométrico real (capa desacoplada; simulador para demostración).
- Días laborales, festivos y descansos (configurables en calendario).

---

## 9. Diagramas complementarios

- `docs/DIAGRAMA_ENTIDAD_RELACION.md`: modelo relacional de la base de datos.
- `docs/DIAGRAMA_FLUJO_ASISTENCIA.md`: flujo de registro de entrada/salida y cálculo de incidencias.

Estos diagramas representan la arquitectura implementada, no una propuesta contradictoria con el código.