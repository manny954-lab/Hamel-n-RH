#!/bin/bash
# =============================================================================
# Hamelín RH - Lanzador de un solo clic (100% offline, sin servidor externo)
#
# Qué hace:
#   1. Crea la base de datos local (SQLite, archivo hamelin_rh.db).
#   2. Inicia la API FastAPI en http://127.0.0.1:8001 (localhost).
#   3. Semilla datos: admin, usuarios de demo, departamentos, horarios y
#      los 45 empleados (APELLIDOS + NOMBRES).
#   4. Abre el cliente de escritorio.
#
# No requiere PostgreSQL, ni conexión a Internet, ni una WiFi específica:
# todo corre en esta máquina sobre localhost, así que al cambiar de red WiFi
# el sistema sigue funcionando al 100%.
# =============================================================================
set -u

cd "/home/Emmanuel/Documentos/OPENCODE" || exit 1

export PYTHONPATH=server
VENV_PY=".venv/bin/python3.9"
[ -x "$VENV_PY" ] || VENV_PY=".venv/bin/python"

echo "=========================================="
echo "  HAMELÍN RH - INICIO (un solo clic)"
echo "=========================================="
echo ""

# ------------------------------------------------------------------ 1. Tablas
echo "[1/4] Creando estructura de base de datos (SQLite local) ..."
"$VENV_PY" -c "from app.core.database import create_tables; create_tables(); print('Tablas listas.')"

# ------------------------------------------------------------------ 2. Servidor
echo "[2/4] Iniciando servidor API en http://127.0.0.1:8001 ..."
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "   El servidor ya está corriendo en el puerto 8001."
else
    nohup "$VENV_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8001 \
        > /tmp/hamelin_server.log 2>&1 &
    echo $! > /tmp/hamelin_server.pid
    for i in $(seq 1 30); do
        if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
            echo "   Servidor listo."
            break
        fi
        sleep 1
    done
fi

# ------------------------------------------------------------------ 3. Semillado
echo "[3/4] Cargando datos de demostración (empleados, usuarios, catálogos) ..."
"$VENV_PY" semillero.py

# ------------------------------------------------------------------ 4. Cliente
echo "[4/4] Abriendo cliente de escritorio ..."
echo ""

if [ -x "./dist/hamelin-rh" ]; then
    # Ejecutable ya compilado (PyInstaller). Se conecta a localhost:8001.
    ./dist/hamelin-rh
else
    echo "   Ejecutable no encontrado, ejecutando desde código fuente..."
    "$VENV_PY" desktop/app/main.py
fi

echo ""
echo "Para detener el servidor: kill $(cat /tmp/hamelin_server.pid 2>/dev/null)"
