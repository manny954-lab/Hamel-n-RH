# CHANGELOG - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Proveedor:** Flautista de Hamelín

---

## [1.0.0] - 2026-10-17

### Primera versión funcional

- Servidor FastAPI + PostgreSQL con SQLAlchemy 2.0 y migraciones Alembic.
- Aplicación de escritorio PySide6 (Qt) con tema oscuro, ejecutable PyInstaller para Linux.
- Autenticación: login, contraseñas con Argon2, JWT, roles, permisos, bloqueo, sesiones, primera administración segura.
- Módulos: usuarios/roles/permisos, empleados, catálogos (departamentos, puestos, horarios, calendarios), registro de asistencia, motor de incidencias, justificantes, notificaciones internas, prenómina revisable, reportes, panel de dirección, auditoría.
- Pruebas automatizadas: 15 casos pasando (autenticación, empleados, asistencia, prenómina).
- Prueba humo de extremo a extremo exitosa contra la API.
- Documentación completa en español (README, manuales, arquitectura, modelo de datos, seguridad, respaldo, infraestructura, cotización).

### Limitaciones conocidas documentadas

- Integración biométrica con dispositivo real no probada (simulador identificado).
- Ejecutable de Windows no construido en este entorno.
- Sin funcionamiento sin conexión ni sincronización automática.
- Precios de hardware son estimaciones preliminares.

---

## Próximas versiones

- Validación de integración biométrica con dispositivo real.
- Construcción y prueba del ejecutable de Windows.
- Ejecución de pruebas de varios clientes simultáneos.
- Validación legal de reglas de cálculo de nómina y descuentos.
