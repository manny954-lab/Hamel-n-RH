# ESTADO DEL PROYECTO - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Fecha:** 17 de octubre de 2026  
**Versión:** 1.0.0

---

## Tareas completadas

- Análisis de requisitos y preguntas pendientes (`docs/ANALISIS_REQUISITOS.md`, `docs/PREGUNTAS_PENDIENTES.md`)
- Arquitectura, modelo de datos y diagramas ER y flujo de asistencia
- Servidor FastAPI + PostgreSQL + SQLAlchemy 2.0 + Alembic (28 tablas, 1 migración)
- Autenticación (Argon2, JWT, roles, permisos, sesiones, auditoría, primer admin seguro)
- API: auth, usuarios, roles/permisos, catálogos, empleados, asistencia, incidencias, justificantes, nómina/prenómina, auditoría, reportes
- Pruebas automatizadas pytest: 15 pasando
- Prueba humo de extremo a extremo exitosa
- Aplicación de escritorio PySide6 con tema oscuro, navegación lateral, login, dashboard, empleados, asistencia, incidencias, justificantes, prenómina, reportes, auditoría, usuarios
- Ejecutable PyInstaller Linux construido y probado (dist/hamelin-rh, 84 MB)
- Documentación: README, manuales, instalación (servidor/Windows/Linux), seguridad, respaldo, infraestructura, cotización, plan y resultados de pruebas, changelog

---

## Tareas pendientes

- Construcción y prueba del ejecutable de Windows (requiere entorno Windows)
- Validación de integración biométrica con dispositivo real
- Pruebas de varios clientes simultáneos
- Restauración de respaldo en producción
- Validación legal de fórmulas de prenómina y descuentos (pendiente del cliente)

---

## Decisiones técnicas

- Python 3.9 (entorno estable con ruedas disponibles) en lugar de 3.14 (falta de ruedas precompiladas)
- pg8000 / psycopg2-binary para PostgreSQL
- JWT con identificador único (jti) para evitar duplicados de sesión
- Modelos heredan de SQLAlchemy DeclarativeBase (`Base`) para registro de tablas
- Tema oscuro por defecto, tema claro opcional documentado

---

## Comandos de ejecución

Servidor:
```bash
PYTHONPATH=server .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Pruebas:
```bash
PYTHONPATH=server .venv/bin/python -m pytest server/tests -v
```

Migraciones:
```bash
PYTHONPATH=. .venv/bin/python -m alembic -c alembic.ini upgrade head
```

Desktop:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python desktop/app/main.py
```
