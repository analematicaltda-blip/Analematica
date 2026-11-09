# Implementación 33 · Fuente de reservas con alcance empresarial

**Avance: 36,11 % (26/72 hitos).** Mejora de la fuente comercial relacionada con ACC-005/ACC-008; no acredita integración fiscal completa ni un nuevo hito.

## Cambios funcionales

La confirmación existente `DomainSargentoReservas.confirm_reservation` ahora requiere actor y prestador explícitos, valida usuario activo y vínculo empresarial independiente vigente, y busca la reserva exclusivamente en el Tenant verificado. No equipara UUID del prestador y empresa ni depende del Tenant ambiental.

Dentro de una transacción bloquea empresa, vínculo, prestador y reserva; vuelve a validar el vínculo después de adquirir los bloqueos. Solo permite PENDING → CONFIRMED. Repetir CONFIRMED devuelve replay; CANCELLED/COMPLETED se rechazan. Un rollback del llamador conserva PENDING. Confirmar no cambia el precio, no factura y no escribe asientos. La creación sigue pendiente: se elimina la respuesta ficticia SIM-123 y se declara `RESERVATION_CREATION_NOT_INTEGRATED`.

El adaptador ERP `SargentoReservas` propaga el contexto al dominio. `ReservationApplicationService` recibe actor/prestador por constructor desde su llamador autenticado, nunca desde metadata del comando; errores de dominio se convierten en códigos acotados, sin exponer detalles internos. Errores inesperados de infraestructura se propagan, sin informar éxito.

## Compatibilidad y límite deliberado

El llamador de `TenienteOperacionComercial` inspeccionado crea el servicio sin contexto autenticado: ahora recibe `AUTHENTICATED_CONTEXT_REQUIRED` y no puede confirmar. Antes de habilitarlo hay que propagar identidad desde una sesión o misión autorizada y comprobar sus autorizaciones; no tomar IDs de actor aportados por el modelo/agente. Este cambio cierra una operación sin alcance explícito, no proporciona permisos nuevos al motor de agentes.

La mejora corresponde al Reservation del dominio business. Existe otro modelo Reservation turístico que no se modifica ni se migra en esta entrega. Falta identificar y verificar los recorridos de producción de ambos sistemas antes de unificarlos.

## Verificación

153 métodos Python aprobados en diez suites. Ocho nuevos cubren confirmación/replay, ausencia de contexto, otro titular, vínculo revocado, reserva de otra empresa, cancelación, rollback y servicio de aplicación sin IDs simulados ni autoridad por metadata. Pruebas sobre tablas ORM reales de una base SQLite aislada.

Evidencia: `evidencias/implementacion-33.json`. Fuente estable; workflow y runner incluyen la suite nueva. No se ha verificado carrera de transición/revocación en PostgreSQL ni interacción completa con los demás flujos operativos. Las pruebas contables previas continúan aprobadas.

## Pendientes

Desglose/revisión fiscal persistentes en la fuente canónica, creación real autorizada con disponibilidad, evidencia de cambios de estado, propagación de identidad confiable en misiones, consumidor fiscal idempotente y vínculo con outbox bajo la misma transacción. Una reserva confirmada todavía no se presenta como venta/factura consumada contablemente. Analemática corporativa y demás criterios de la matriz siguen pendientes.

Sin modificaciones de datos del usuario, commit, push o despliegue.
