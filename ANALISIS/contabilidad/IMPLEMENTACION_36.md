# Implementación 36 · Visibilidad de la cola comercial y límites del consumidor

**Avance: 36,11 % (26/72 hitos).** Amplía ACC-008, ya puntuado. No acredita consumidor fiscal ni aceptación completa.

## Implementación

El núcleo compartido incorpora `inspect_commercial_outbox`: consulta contadores por empresa y tipo permitido de evento, sin modificar filas. Separa solicitudes de factura y confirmaciones de reserva. Agrupa estados de transporte PENDING/PROCESSED/ERROR; estados desconocidos se cuentan como OTHER, sin devolver su contenido. Omite payloads, importes, documentos, actores, llaves e identificadores de solicitudes individuales.

El ERP expone `GET /api/v1/mi-negocio/contable/contabilidad/cuentas/estado-cola-comercial/?provider_id=<UUID>`. Reutiliza la autenticación y el vínculo empresarial vigente del titular de `PlanCuentaViewSet`; no permite seleccionar directamente un Tenant arbitrario. El helper interno por sí mismo no autentica usuarios y solo debe invocarse desde un contexto autorizado.

La respuesta declara consulta de solo lectura, consumidor fiscal no integrado, acuse no verificado y aceptación NOT_VERIFIED. Un registro PROCESSED del outbox nunca se interpreta como aceptación DIAN o como asiento. Los contadores son de transporte, no validación semántica de cada payload ni certificación de integridad del evento.

## Verificación

160 métodos Python aprobados en diez suites. Cuatro pruebas nuevas verifican: eventos operativos/comerciales ignorados por el proyector contable sin acuse o publicación; PROCESSED sin aceptación fiscal; aislamiento empresarial y omisión de payloads; rechazo de otro titular o vínculo revocado.

La separación por tipo de evento ya existía en el proyector; no se atribuye esta propiedad a una corrección nueva. Esta entrega añade observabilidad y regresiones explícitas para los nuevos productores.

Evidencia: `evidencias/implementacion-36.json`, fuente estable. PostgreSQL no se repitió: no cambiaron bloqueos o esquema; la consulta agrupada está verificada aquí sobre ORM/SQLite aislado. Faltan volumen/índices/plan de consulta PostgreSQL y recorrido de navegador para esta ruta nueva.

## Pendientes

Consumidor fiscal persistente con recibos idempotentes, error/reintento y acuses de habilitación reales; origen fiscal revisado; autorización y límites de publicación; panel web para estos contadores, integración corporativa Analemática y operación con credenciales reales. No se ha añadido un dispatcher genérico que marque eventos no atendidos como procesados. Un contador vacío no significa que el ciclo comercial esté completo.

Sin cambios de datos del usuario, commit, push o despliegue.
