# INSTALACIÓN EN WINDOWS - Hamelín RH (cliente)

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

Este documento describe la instalación del cliente de escritorio en Windows.

---

## Requisitos

- Windows 10 o Windows 11 (64 bits)
- Acceso de red al servidor de la API (puerto 8001 por defecto)
- Pantalla mínima 1280x720

---

## Instalación

1. Obtener el ejecutable generado con PyInstaller (`dist/hamelin-rh.exe`).
   - El ejecutable de Windows debe construirse en un entorno Windows; no funciona en Linux.
2. Copiar `hamelin-rh.exe` a la computadora cliente.
3. Crear un acceso directo en el escritorio o menú de inicio.
4. Ejecutar `hamelin-rh.exe`.

---

## Configuración del servidor

Al iniciar, el cliente intenta conectar a `http://127.0.0.1:8001`. Si el servidor está en otra computadora, configurar la URL de la API desde el cliente (pantalla de conexión o archivo de configuración).

Si el servidor no está disponible, el cliente muestra un mensaje claro en español y no permite operaciones que requieran la base de datos central.

---

## Mensajes si el servidor no está disponible

- "No se puede conectar al servidor de la API. Verifique la URL y que el servidor esté en ejecución."
- Todas las operaciones de lectura/escritura se bloquean hasta restablecer la conexión.

---

## Procedimiento de actualización

1. Detener el cliente.
2. Reemplazar `hamelin-rh.exe` por la nueva versión generada con PyInstaller.
3. Volver a ejecutar.

No se requiere desinstalación previa si se usa el ejecutable directo.

---

## Notas

- No se asume que un ejecutable de Windows funcione en Linux.
- La aplicación no requiere navegador web; es un programa de escritorio nativo.
