# Implementación 31 · Persistencia transaccional de solicitudes de factura

**Avance: 36,11 % (26/72 hitos).** ACC-008 amplía un incremento ya puntuado; no se agregan hitos ni aceptación completa.

## Servicio interno compartido

`invoice_queue.enqueue_invoice_intent` valida el contrato versionado, empresa activa y actor activo, bloquea la fila de empresa y registra el request en el OutboxEvent existente. La identidad determinista usa un UUID v5 con namespace específico y la clave del contrato; no requiere migraciones nuevas.

El método participa en la transacción externa del productor sobre la misma conexión predeterminada. Si esa transacción revierte, desaparece la solicitud. No ofrece atomicidad entre bases distintas. La repetición exacta devuelve el registro existente; contenido, actor o metadatos incompatibles bajo la misma identidad generan conflicto sin sobrescritura. Una revisión diferente obtiene identidad distinta. El bloqueo empresarial serializa solicitudes de la misma empresa; su coste bajo carga sigue pendiente.

La respuesta distingue persistencia local, replay y estado actual del outbox. Indica `published_by_this_call=false`: no afirma que otro proceso jamás haya publicado ese registro. Un replay conserva un estado PROCESSED existente, sin resetearlo. No hay llamadas a bus, red, DIAN, bancos o pagos ni callbacks automáticos de publicación desde este servicio.

El payload contiene identificadores y metadatos financieros mínimos del contrato, no XML/PDF, documentos fiscales, KEK o archivos. Esto no demuestra conocimiento cero de todo el ERP.

## Verificación

- 142 métodos Python aprobados en nueve suites: ocho nuevos de persistencia/rollback/replay/conflicto, revisión, actor y empresa, fallos de escritura y conservación del estado del outbox.
- 22 escenarios contables PostgreSQL aprobados: dos nuevos con conexiones independientes compiten por solicitudes idénticas o incompatibles. En ambos casos queda un solo request; las idénticas devuelven una inserción y un replay; las incompatibles aceptan solo una.
- La restauración del ledger también incluye los nuevos requests y conserva los datos del origen.
- 14 pruebas del verificador local aprobadas; evidencia: `evidencias/implementacion-31.json`.

## Límites de autorización e integración

Este servicio es interno y todavía no está expuesto por rutas o conectado a señales/modelos CRM. Un actor activo no acredita permiso comercial sobre una empresa. El productor deberá autenticar y autorizar al solicitante, bloquear/leer el origen real y verificar estado/revisión antes de llamar dentro de su transacción. No aceptar directamente snapshots de usuarios para emitir solicitudes fiscales.

Pendientes: productores de ambos sistemas, recibo idempotente del consumidor, canal de publicación y control de errores/leases, habilitación y acuses fiscales reales, reglas tributarias revisadas, permisos SQL del despliegue y rendimiento. El outbox existente no es un registro criptográficamente inmutable contra operadores privilegiados. No se acredita factura emitida, cobro o asiento por persistir el request.

Sin cambios de datos del usuario, commit, push o despliegue.
