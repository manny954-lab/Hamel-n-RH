# INSTALACIÓN DEL SERVIDOR - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

Este documento describe la instalación reproducible del servidor (API FastAPI + PostgreSQL).

---

## Requisitos del servidor

- Sistema operativo: Linux recomendado (Debian/Ubuntu/Fedora) o Windows Server
- Python 3.9+
- PostgreSQL 14+
- Acceso de red desde los clientes al puerto de la API (8001 por defecto)

---

## 1. Instalar PostgreSQL

```bash
# Ejemplo en Fedora/RHEL
sudo dnf install -y postgresql-server postgresql-devel
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

Crear la base de datos y un usuario dedicado:

```sql
CREATE DATABASE hamelin_rh;
CREATE USER hamelin_rh_app WITH PASSWORD 'cambiar_esta_contraseña';
GRANT ALL PRIVILEGES ON DATABASE hamelin_rh TO hamelin_rh_app;
```

Ajustar `pg_hba.conf` para permitir conexiones de la API y reiniciar PostgreSQL.

---

## 2. Preparar la aplicación

```bash
cd /opt/hamelin-rh   # o la carpeta de instalación
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r server/requirements.txt
```

Copiar el archivo de entorno:

```bash
cp server/.env.example server/.env
```

Editar `server/.env` con valores reales de producción:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `DATABASE_URL` (formato `postgresql+psycopg2://user:pass@host:port/db`)
- `SECRET_KEY` (generar con `openssl rand -hex 32`)
- `ENVIRONMENT=production`
- `LOG_LEVEL=WARNING` o `INFO`

**No subir `server/.env` al control de versiones.**

---

## 3. Crear la base de datos y aplicar migraciones

```bash
PYTHONPATH=. .venv/bin/python -m alembic -c alembic.ini upgrade head
```

Esto crea todas las tablas versionadas. Verificar:

```bash
PYTHONPATH=. .venv/bin/python -c "from app.core.database import Base; print(len(Base.metadata.tables), 'tablas')"
```

---

## 4. Crear el primer administrador (procedimiento seguro)

No existe una cuenta administrativa universal. El primer administrador debe crearse de forma segura:

```bash
curl -X POST http://localhost:8001/api/v1/auth/first-admin \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin.coolcircle",
    "nombre_completo": "Administrador del Sistema",
    "email": "admin@coolcircle.mx",
    "password": "ClaveSegura2026!"
  }'
```

Este endpoint solo funciona si no existe ningún usuario. Tras crear al primer administrador, se deshabilita el auto-registro. Obliga a establecer credenciales propias.

---

## 5. Iniciar y detener el servicio

Iniciar la API:

```bash
PYTHONPATH=server .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Para producción, usar un gestor de procesos (systemd) y un proxy inverso (Nginx) con TLS.

Ejemplo de unidad systemd (`/etc/systemd/system/hamelin-rh.service`):

```ini
[Unit]
Description=Hamelín RH API
After=network.target postgresql.service

[Service]
Type=simple
User=hamelin
WorkingDirectory=/opt/hamelin-rh
Environment=PYTHONPATH=/opt/hamelin-rh/server
ExecStart=/opt/hamelin-rh/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now hamelin-rh
```

---

## 6. Configurar el firewall

Permitir el puerto de la API solo desde la red local:

```bash
# Ejemplo firewalld
sudo firewall-cmd --permanent --add-port=8001/tcp --zone=trusted
sudo firewall-cmd --reload
```

En producción, exponer la API solo a través de HTTPS (Nginx + Let's Encrypt o certificado interno).

---

## 7. Prueba de conexión desde clientes

Desde una computadora cliente:

```bash
curl http://<servidor>:8001/health
```

Debe responder `{"status":"ok","service":"hamelin-rh-api"}`.

---

## 8. Respaldos y restauración

Ver `docs/RESPALDO_Y_RESTAURACION.md`.

Ejemplo de respaldo diario:

```bash
pg_dump -h localhost -U hamelin_rh_app hamelin_rh > /destino/externo/hamelin_rh_$(date +%F).sql
```

---

## 9. Comprobación de despliegue seguro

- [ ] `SECRET_KEY` cambiada del valor por defecto
- [ ] `ENVIRONMENT=production`
- [ ] Sin credenciales en el repositorio
- [ ] Firewall restringe el puerto de la API
- [ ] Comunicación cifrada (TLS) en producción
- [ ] Copia de seguridad probada (restauración en entorno aislado)
- [ ] Primer administrador creado con credenciales propias
