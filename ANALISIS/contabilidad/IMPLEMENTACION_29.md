# Implementación 29 · Revocación y desconexión documental

**Avance: 33,33 % (24/72 hitos).** Verificación adicional de ACC-011; no agrega hitos ni aceptación completa.

## Comportamiento comprobado

Se amplió el contrato PostgreSQL del almacén documental con revocación real de permisos SQL sobre el rol limitado, conservando abierta su conexión. Al retirar INSERT, incluso repetir un sobre existente falla con permiso denegado; no se devuelve un éxito idempotente ficticio. La lectura permitida continúa funcionando. Al retirar SELECT, recuperar el documento falla. El adaptador no cambia de rol ni usa la conexión propietaria como alternativa. El rol propietario solo interviene en el montaje y recuperación de permisos de esta fixture.

A continuación se termina explícitamente la sesión PostgreSQL del escritor. La siguiente escritura falla y no se informa almacenamiento exitoso. Después de cerrar la conexión fallida y reconectar explícitamente, repetir el sobre devuelve replay, los dos documentos siguen idénticos y el conteo permanece en dos. El adaptador no reintenta automáticamente operaciones cuyo resultado pudiera ser incierto.

También se repite la recuperación documental en una base nueva, con controles SQL conservados.

## Evidencia

127 métodos Python aprobados y 20 escenarios contables PostgreSQL aprobados. El escenario BYOS incluye ahora cuatro comprobaciones adicionales: INSERT revocado, SELECT revocado, sesión desconectada y reconexión sin duplicado. Se conserva el número de escenarios para no presentar subcomprobaciones como escenarios nuevos.

Evidencia: `evidencias/implementacion-29.json`; código en `BACKEND/deployment/tests/customer_byos_contract.py`. Fuente estable durante la ejecución.

## Límites

Una sesión terminada reproduce pérdida de conexión, no todos los fallos de red: faltan particiones, latencia, timeouts operativos, fallos en el punto exacto entre commit y respuesta, retención de conexiones y recuperación a gran escala. La revocación SQL no acredita revocación OAuth ni retira copias ya descargadas. No se invalidan llaves del cliente ni se borra su información.

BYOS permanece parcial y sin conexión a formularios/API de producción. Continúan pendientes los demás proveedores, custodia y recuperación real de KEK, propiedad del destino, roles productivos y aceptación de ambos sistemas. Sin commit, push o despliegue.
