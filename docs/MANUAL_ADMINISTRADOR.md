# MANUAL DEL ADMINISTRADOR - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0  
**Idioma:** español de México

---

## 1. Creación del primer administrador

No existe una cuenta administrativa universal. Tras instalar el servidor, ejecute:

```bash
curl -X POST http://<servidor>:8001/api/v1/auth/first-admin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","nombre_completo":"Nombre","email":"admin@empresa.mx","password":"ClaveSegura2026!"}'
```

Este endpoint solo funciona si no hay usuarios creados. Obliga a establecer credenciales propias.

---

## 2. Usuarios, roles y permisos

- Crear usuarios desde el módulo Usuarios (requiere permiso).
- Asignar roles a los usuarios.
- Configurar permisos por rol, módulo y operación.
- Un usuario no puede elevar sus propios privilegios.
- Las cuentas se desactivan, no se borran, conservando el historial.

---

## 3. Empleados

- Alta, edición y baja administrativa de empleados.
- Asignar departamento, puesto y horario con fecha de vigencia.
- Configurar sueldo base y periodicidad (mensual, quincenal, semanal, etc.).
- Importar desde CSV con validación previa.
- Detectar números de empleado duplicados.

---

## 4. Horarios y calendarios

- Crear departamentos, puestos y horarios (entrada, salida, tolerancia, días laborables).
- Asignar horarios individualmente o colectivamente con vigencia.
- Definir días festivos y días de descanso.
- Soporta turnos que cruzan medianoche (preparado, no necesario en el primer escenario).

---

## 5. Tolerancia e incidencias

- Configurar la tolerancia de entrada (inicialmente 10 minutos).
- Configurar la regla "tres retardos equivalen a una falta" (periodo por definir).
- Ninguna falta se convierte en descuento automático ni baja sin revisión humana.
- Todas las incidencias muestran la regla aplicada.

---

## 6. Justificantes

- Tipos: médico, legal, parte de tránsito, otro configurable.
- Estados: pendiente, en revisión, aprobada, rechazada, cancelada.
- Solo usuarios autorizados aprueban o rechazan.
- Proteger archivos adjuntos; no mostrar diagnósticos médicos a usuarios sin autorización.

---

## 7. Prenómina

- Configurar sueldo base y periodicidad por empleado con fecha de vigencia.
- Definir periodos de nómina.
- Calcular prenómina revisable.
- Aprobar o rechazar propuestas de ajuste con motivo.
- Cerrar periodo mediante proceso autorizado.
- Modificaciones tras el cierre requieren autorización y quedan auditadas.

---

## 8. Seguridad

- Cambiar la `SECRET_KEY` de producción.
- Configurar `ENVIRONMENT=production`.
- Habilitar HTTPS/TLS en producción.
- Configurar firewall para restringir el puerto de la API.
- No conectar clientes directamente a PostgreSQL.
- Configurar copias de seguridad automatizadas con destino externo.
- Probar restauraciones periódicamente.

---

## 9. Auditoría

Revisar periódicamente el registro de operaciones sensibles (solo lectura para usuarios ordinarios).

---

## 10. Respaldos y restauración

Ver `docs/RESPALDO_Y_RESTAURACION.md`.

---

## 11. Actualizaciones

- Detener el servidor.
- Aplicar migraciones: `alembic upgrade head`.
- Reiniciar el servidor.
- Distribuir nuevos ejecutables de cliente generados con PyInstaller.
