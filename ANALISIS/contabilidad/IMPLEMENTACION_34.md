# Implementación 34 · Concurrencia de la fuente de reservas

**Avance: 36,11 % (26/72 hitos).** Refuerza la verificación de ACC-005/ACC-008 sin incrementar hitos ya acreditados.

## Verificación real PostgreSQL

Se extendió el perfil aislado para crear registros reales de prestador, identidad empresarial revisada y reserva del dominio business en una base PostgreSQL desechable. Usa los servicios de revisión y confirmación existentes; no reemplaza sus decisiones por mocks.

Dos conexiones independientes solicitan simultáneamente confirmar una reserva PENDING. Ambas obtienen una respuesta coherente: una transición y un replay. La reserva termina CONFIRMED, sin emisión fiscal o asiento.

En el segundo escenario se pausa la confirmación después de resolver inicialmente el vínculo, antes del bloqueo de empresa. Otra conexión revoca y confirma la revocación en la base. Al continuar, el servicio adquiere sus bloqueos, revalida el permiso y rechaza la confirmación; la reserva permanece PENDING. La pausa usa eventos de sincronización de la prueba, sin sleeps. No se simula la decisión de permisos.

El perfil también restaura en otra base el conjunto ampliado y compara su manifiesto, controles e integridad; el origen permanece sin cambios.

## Resultados

153 métodos Python contables y 24 escenarios contables PostgreSQL aprobados. Dos escenarios nuevos se identifican como `reservation_source_duplicate_confirmation` y `reservation_source_revoke_after_initial_read`. Las 14 pruebas del verificador local también pasaron.

Evidencia: `evidencias/implementacion-34.json`. Fuente estable durante la ejecución. Se mantiene la evidencia anterior; esta entrega no acredita ambos sistemas completos ni permisos productivos.

## Límites y trabajo restante

La prueba demuestra revocación ya confirmada antes de la segunda validación. No cubre todos los órdenes posibles de revocación, transferencia de titularidad, desactivación del usuario/revisor, cancelación concurrente o ejecución desde colas distribuidas. Una operación ya confirmada antes de la revocación no se revierte automáticamente. Faltan auditoría persistente de transiciones, desglose/revisión fiscal canónicos y conexión autorizada al outbox de facturación. El otro modelo Reservation turístico no se unifica con esta prueba.

Las nuevas tablas existen únicamente dentro del montaje de pruebas y se eliminan con la base temporal. No se aplican migraciones a datos del usuario ni se habilitan agentes. Sin commit, push o despliegue.
