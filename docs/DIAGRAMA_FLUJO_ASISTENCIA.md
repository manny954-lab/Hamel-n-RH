# DIAGRAMA DE FLUJO DE ASISTENCIA - Hamelín RH

**Producto:** Hamelín RH  
**Cliente:** Cool Circle  
**Versión:** 1.0  
**Estado:** Representa el flujo implementado en los módulos de registro de asistencia y motor de incidencias.

---

## 1. Flujo de registro de entrada/salida (Mermaid)

```mermaid
flowchart TD
    A[Inicio: operador abre módulo Registro de asistencia] --> B{¿Usuario tiene permiso asistencia.registrar?}
    B -- No --> C[Mostrar error: permisos insuficientes]
    B -- Sí --> D[Buscar empleado por número o nombre]
    D --> E{¿Empleado existe y está activo?}
    E -- No --> F[Mostrar error: empleado no encontrado o inactivo]
    E -- Sí --> G[Seleccionar tipo evento: Entrada / Salida]
    G --> H[Capturar evento: empleado, dispositivo, método]
    H --> I[Enviar a API POST /api/v1/asistencia/eventos]
    I --> J[Servidor valida token JWT y permisos]
    J --> K[Servidor verifica horario asignado del empleado]
    K --> L[Detección de duplicados y eventos imposibles]
    L --> M{¿Evento válido?}
    M -- No --> N[Registrar evento con resultado_validacion = duplicado/imposible]
    N --> O[Mostrar advertencia al operador]
    M -- Sí --> P[Motor de incidencias calcula retardo/incidencia según tolerancia]
    P --> Q[Persistir evento_asistencia e incidencia si aplica]
    Q --> R[Escribir registro en auditoría]
    R --> S[Crear notificación interna si incidencia requiere intervención RRHH]
    S --> T[Responder al cliente con evento creado o error]
    T --> U[Mostrar mensaje de éxito o advertencia en pantalla]

    style A fill:#2d3436,color:#fff
    style U fill:#00b894,color:#fff
    style C fill:#d63031,color:#fff
    style F fill:#d63031,color:#fff
    style O fill:#fdcb6e,color:#000
```

---

## 2. Flujo de cálculo de incidencia (motor de reglas)

```mermaid
flowchart TD
    A[Evento de entrada detectado] --> B[Obtener horario asignado vigente al empleado]
    B --> C[Comparar hora real vs hora de entrada del horario]
    C --> D{¿Hora real <= entrada + tolerancia?}
    D -- Sí --> E[Sin incidencia: entrada dentro de tolerancia]
    D -- No --> F[Calcular minutos de retardo = hora_real - hora_entrada]
    F --> G[Crear incidencia tipo retardo con minutos y regla_aplicada]
    G --> H[¿Existen 3 retardos en el periodo configurado?]
    H -- Sí --> I[Proponer falta por acumulación de retardos regla configurable]
    H -- No --> J[Fin]
    I --> K[Estado pendiente, notificar a RRHH para revisión humana]

    subgraph Reglas configurables
    T[Tolerancia inicial: 10 minutos]
    U[Tres retardos = una falta periodo por definir]
    end
    T -.-> D
    U -.-> H
```

---

## 3. Flujo de justificación de incidencia

```mermaid
flowchart TD
    A[Empleado o RRHH registra justificante] --> B[Tipo: médico / legal / tránsito / otro]
    B --> C[Adjuntar documentación opcional acceso restringido]
    C --> D[Estado: pendiente]
    D --> E[RRHH revisa y comunica con el trabajador]
    E --> F{Decisión}
    F -- Aprobar --> G[Estado: aprobada, incidencia marcada como justificada]
    F -- Rechazar --> H[Estado: rechazada con motivo]
    F -- Solicitar información --> I[Estado: en revisión, notificar al empleado]
    G --> J[Motor recalcula incidencia si aplica]
    H --> K[Conservar historial de decisión]
    I --> K
    J --> L[Escribir en auditoría]
```

---

## 4. Flujos de prenómina

```mermaid
flowchart TD
    A[Abrir periodo de nómina estado abierto] --> B[Consultar incidencias del periodo]
    B --> C[Calcular sueldo base por periodicidad y vigencia]
    C --> D[Calcular minutos de retardo, faltas, justificadas]
    D --> E[Proponer ajustes económicos según conceptos configurados]
    E --> F[Mostrar cálculo paso a paso prenómina revisable]
    F --> G[RRHH/Nómina aprueba o rechaza ajustes]
    G --> H[Registrar ajustes aprobados con motivo]
    H --> I[Generar vista previa y exportar resumen]
    I --> J[Cerrar periodo proceso autorizado]
    J --> K[Modificaciones posteriores requieren autorización y auditoría]
```

---

## 5. Reglas de negocio clave del flujo

1. **Tolerancia:** 10 minutos iniciales. Se documenta si el minuto límite está dentro o fuera de la tolerancia (valor provisional: minuto 11 está fuera).
2. **Tres retardos = una falta:** regla configurable, periodo por definir (valor demo: quincena).
3. **No descuento automático:** ninguna falta o retardo se convierte en descuento salarial sin revisión humana y autorización.
4. **Justificantes:** aprobados solo por usuarios autorizados; protegen datos sensibles (no mostrar diagnósticos médicos a quien solo consulta estado).
5. **Historial inalterable:** los eventos de asistencia no se borran silenciosamente; las correcciones generan ajustes con valor anterior, valor corregido, motivo, fecha y responsable.
6. **Detección de anomalías:** duplicados, eventos imposibles y entradas sin salida asociada se detectan y marcan.

---