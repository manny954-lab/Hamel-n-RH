# RESPALDO Y RESTAURACIÓN - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

---

## 1. Política de respaldos

| Elemento | Valor |
|---|---|
| Frecuencia | Diaria (recomendada) y antes de operaciones destructivas |
| Retención | Al menos 30 días (ajustable según política del cliente) |
| Destino | Medio externo o destino independiente al disco del servidor |
| Cifrado | Sí, los respaldos deben cifrarse |
| Procedimiento de recuperación | Documentado y probado periódicamente |

El destino de respaldo **no debe depender exclusivamente del mismo disco del servidor**.

---

## 2. Qué se respalda

- Base de datos PostgreSQL `hamelin_rh` (esquema y datos).
- Archivos adjuntos de justificantes (directorio configurado en `ADJUNTOS_DIR`).
- Archivos de configuración (`server/.env`, `alembic.ini`, certificados TLS).
- Scripts de despliegue y migraciones.

---

## 3. Procedimiento de respaldo (ejemplo)

```bash
#!/bin/bash
# respaldo_hamelin.sh
FECHA=$(date +%F_%H-%M)
DESTINO="/mnt/respaldo-externo/hamelin_rh"
mkdir -p "$DESTINO"

# Base de datos
pg_dump -h localhost -U hamelin_rh_app hamelin_rh | gzip > "$DESTINO/bbdd_$FECHA.sql.gz"

# Adjuntos
tar -czf "$DESTINO/adjuntos_$FECHA.tar.gz" -C /opt/hamelin-rh/server data/adjuntos

# Configuración
tar -czf "$DESTINO/config_$FECHA.tar.gz" -C /opt/hamelin-rh server/.env alembic.ini

echo "Respaldo completado: $FECHA"
```

El script debe ser idempotente y explicar sus efectos antes de operaciones destructivas.

---

## 4. Procedimiento de restauración

1. Detener el servidor de la API.
2. Restaurar la base de datos:

```bash
gunzip < bbdd_FECHA.sql.gz | psql -h localhost -U hamelin_rh_app hamelin_rh
```

3. Restaurar adjuntos y configuración si es necesario.
4. Verificar migraciones aplicadas:

```bash
PYTHONPATH=server .venv/bin/python -m alembic -c alembic.ini upgrade head
```

5. Iniciar el servidor y probar la conexión desde un cliente.

---

## 5. Pruebas de restauración

- Probar la restauración en un entorno aislado al menos una vez al mes.
- Verificar integridad de datos críticos (empleados, asistencia, incidencias, prenómina).
- Documentar el resultado de cada prueba.

---

## 6. Protección frente a borrado accidental

- Eliminación lógica en tablas maestras (empleados, departamentos, etc.).
- Las correcciones de asistencia generan ajustes con valor anterior y nuevo (no se borran eventos silenciosamente).
- La auditoría es de solo lectura.

---

## 7. Retención de datos

Definida en `configuracion_general` y sujeta a la política del cliente y la legislación laboral mexicana.
