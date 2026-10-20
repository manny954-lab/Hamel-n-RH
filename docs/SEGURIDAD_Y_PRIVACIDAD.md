# SEGURIDAD Y PRIVACIDAD - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0

---

## 1. Contraseñas

- Las contraseñas se almacenan únicamente como hash seguro usando **Argon2** (vía passlib), nunca en texto plano.
- No hay contraseñas predeterminadas permanentes.
- El primer administrador debe establecer sus propias credenciales mediante el procedimiento seguro de creación (`/api/v1/auth/first-admin`).
- Los usuarios pueden cambiar su contraseña; un administrador autorizado puede restablecerla.
- No se guardan credenciales en el repositorio ni en variables de entorno incluidas en Git (`.env.example` solo con valores ficticios).

---

## 2. Control de acceso

- Autorización basada en roles y permisos (RBAC), verificada en el **servidor** por cada operación sensible.
- Los roles son configurables y sus permisos ajustables por módulo y operación.
- Un usuario no puede elevar sus propios privilegios.
- Un supervisor no accede a departamentos ajenos salvo autorización explícita.
- Las cuentas se desactivan (no se borran), conservando su historial.

---

## 3. Comunicación cifrada

- Los clientes se comunican con la API mediante HTTP (desarrollo) o **HTTPS/TLS** (producción).
- No existen conexiones directas de las computadoras cliente a PostgreSQL; solo la API privada autorizada.
- Tokens JWT con expiración y revocación de sesiones.

---

## 4. Validación de entradas

- Validación en el servidor con Pydantic.
- Consultas parametrizadas mediante SQLAlchemy ORM (protección contra inyección SQL).
- Manejo centralizado de errores.

---

## 5. Sesiones

- Vencimiento de sesión por inactividad (configurable).
- Bloqueo temporal tras varios intentos fallidos de login (configurable).
- Registro de accesos exitosos y fallidos.

---

## 6. Protección de documentos adjuntos

- Los justificantes pueden tener documentación adjunta con acceso restringido.
- Los archivos sensibles no se incluyen en exportaciones generales.
- No se muestran diagnósticos médicos ni contenido sensible a usuarios que solo necesitan conocer el estado de la incidencia.

---

## 7. Auditoría

- Registro de operaciones sensibles: login/logout, altas y modificaciones de empleados, cambios de sueldo y horario, correcciones de asistencia, aprobaciones/rechazos, cambios de permisos, exportaciones, cambios de configuración, operaciones de prenómina y cierres de periodo.
- Cada registro contiene usuario, fecha/hora, operación, entidad, identificador, motivo y resultado.
- La auditoría es de solo lectura para usuarios ordinarios y protegida frente a modificaciones no autorizadas.
- Nunca se almacenan contraseñas ni datos biométricos en la auditoría.

---

## 8. Datos biométricos

- Por defecto, **no se almacenan imágenes de huellas ni plantillas biométricas** en la base de datos central.
- Se prioriza la verificación local del dispositivo y el almacenamiento de un identificador de evento, resultado de validación y datos mínimos.
- La capa de integración biométrica está desacoplada para distintos fabricantes.
- Si se requiere almacenar plantillas, exige una evaluación específica de seguridad, privacidad, consentimiento y obligaciones legales antes de implementarlo (ley mexicana de protección de datos personales).
- Incluye alternativa de registro manual autorizado y auditable.
- El simulador biométrico está claramente identificado y nunca se presenta como dispositivo real.

---

## 9. Datos personales y salariales

- Se recopila solo la información necesaria para la operación (nombre, departamento, puesto, horario, sueldo base con vigencia).
- Los cambios salariales y contractuales guardan fecha de vigencia e historial.
- La información salarial respeta los permisos del usuario en reportes y exportaciones.

---

## 10. Obligaciones legales (México)

- El tratamiento de datos personales está sujeto a la Ley Federal de Protección de Datos Personales en Posesión de los Particulares y su Reglamento.
- Se recomienda validación profesional (legal y de protección de datos) antes de poner en producción, especialmente para datos biométricos y salariales.

---

## 11. Copias de seguridad

- Automatizadas, con destino externo al servidor, cifrado y procedimiento de restauración.
- Pruebas de restauración periódicas.

Ver `docs/RESPALDO_Y_RESTAURACION.md`.

---

## 12. Checklist de despliegue seguro

- [ ] Contraseñas con hash Argon2
- [ ] `SECRET_KEY` cambiada y protegida
- [ ] Variables de entorno fuera del repositorio
- [ ] Comunicación cifrada (TLS) en producción
- [ ] Firewall configurado
- [ ] Clientes sin acceso directo a PostgreSQL
- [ ] Auditoría habilitada y de solo lectura
- [ ] Copias de seguridad automatizadas y probadas
- [ ] Entornos de desarrollo y producción separados
