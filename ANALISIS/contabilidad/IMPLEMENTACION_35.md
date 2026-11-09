# Implementación 35 · Evento durable de confirmación de reserva

**Avance: 36,11 % (26/72 hitos).** Se amplía ACC-008, ya puntuado, sin acreditar otro hito ni aceptación completa.

## Cambio funcional

La transición autorizada PENDING → CONFIRMED del modelo domain_business.Reservation guarda ahora un evento `operations.reservation.confirmed.v1` en el outbox existente, dentro de la misma transacción. El evento identifica empresa, prestador, reserva, actor y estados anterior/nuevo. Su UUID determinista usa un namespace separado. No contiene documentos fiscales o llaves, no llama al bus ni publica desde este servicio.

Si falla la persistencia del evento, la reserva permanece PENDING. Si falla la transacción externa del productor, se revierten estado y evento. El replay de una confirmación nueva conserva un único evento. La concurrencia PostgreSQL produce una transición y un evento con dos respuestas coherentes.

Un evento incompatible bajo la misma identidad genera error y no se sobrescribe. Un evento existente para una reserva todavía PENDING también bloquea la transición y exige revisión. No se fabrican eventos retrospectivos: una reserva antigua ya CONFIRMED sin evento devuelve replay con `confirmation_event_recorded=false` e identificador nulo.

La respuesta diferencia evento registrado y publicación por esta llamada. El payload incluye `fiscal_ready=false`: el evento no demuestra revisión tributaria, factura, cobro ni asiento. Se mantiene `ledger_written=false`.

## Verificación

156 métodos Python aprobados en diez suites. Tres pruebas adicionales cubren fallo del evento con rollback, legado sin historial fabricado y conflicto sin sobrescritura. Se ampliaron pruebas existentes de replay y rollback externo.

24 escenarios contables PostgreSQL aprobados. El escenario de confirmación simultánea verifica también un solo evento durable y la misma referencia en ambas respuestas; el de revocación verifica ausencia de eventos. El respaldo/restauración compara el conjunto ampliado sin modificar el origen. Las 14 pruebas del verificador local también pasaron.

Evidencia: `evidencias/implementacion-35.json`; fuente estable. No se crean tablas ni migraciones nuevas.

## Pendientes

El outbox existente es mutable para procesos privilegiados: no equivale a auditoría criptográfica inmutable, firma o prueba fiscal. Faltan consumidor deduplicado, revisión de publicación/retención, reglas de acceso al evento y tratamiento de legados con evidencia independiente. No reconstruir historia automáticamente ni usar un evento ausente como autorización para reemitir.

Pendientes también desglose/revisión fiscal persistentes, conexión al contrato de invoice intent desde fuentes reales autorizadas, propagación de contexto confiable en agentes, modelo Reservation turístico alternativo y recorrido corporativo Analemática. Confirmar operativamente sigue separado del reconocimiento contable/fiscal definitivo; no se afirma cumplimiento integral de ledger-first.

Sin cambios de datos del usuario, commit, push o despliegue.
