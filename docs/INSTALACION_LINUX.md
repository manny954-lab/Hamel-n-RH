# INSTALACIÓN EN LINUX - Hamelín RH (cliente)

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

Este documento describe la instalación del cliente de escritorio en Linux.

---

## Requisitos

- Distribución Linux compatible (probado en Fedora)
- Bibliotecas del sistema necesarias para Qt (generalmente incluidas en el ejecutable de PyInstaller)
- Acceso de red al servidor de la API (puerto 8001 por defecto)

---

## Instalación

1. Obtener el ejecutable generado con PyInstaller en Linux (`dist/hamelin-rh`).
2. Otorgar permiso de ejecución:

```bash
chmod +x hamelin-rh
```

3. Ejecutar:

```bash
./hamelin-rh
```

O crear un archivo `.desktop` para acceder desde el entorno de escritorio:

```ini
[Desktop Entry]
Name=Hamelín RH
Exec=/ruta/a/hamelin-rh
Icon=hamelin-rh
Type=Application
Categories=Office;
```

---

## Configuración del servidor

Al iniciar, el cliente intenta conectar a `http://127.0.0.1:8001`. Ajustar la URL si el servidor está en otra computadora.

Si el servidor no está disponible, el cliente muestra un mensaje claro en español.

---

## Dependencias del sistema (si se ejecuta desde código fuente)

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r desktop/requirements.txt
QT_QPA_PLATFORM=offscreen .venv/bin/python desktop/app/main.py
```

En entornos con servidor gráfico, omitir `QT_QPA_PLATFORM=offscreen`.

---

## Procedimiento de actualización

1. Detener el cliente.
2. Reemplazar el ejecutable por la nueva versión.
3. Volver a ejecutar.
