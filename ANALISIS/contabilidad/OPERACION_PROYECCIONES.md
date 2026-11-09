# Operación del consumidor contable local

Código: `BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/delivery.py`. Destino interno fijo: `accounting.daily-balance.v1`. No admite URLs, comandos, módulos ni consumidores suministrados por el payload. No tiene transporte de red ni realiza pagos.

## Preparación

La migración aditiva `core_erp.0003_accounting_projection` crea trabajos, recibos y saldos diarios derivados. Está disponible en el grafo original y en fresh-local. Requiere `0002_ledger_posting_v2`; no cambia hashes/asientos históricos ni marca eventos como publicados.

Se aplicó y verificó únicamente en la base temporal de desarrollo. Antes de una base existente: copia, revisión del grafo, migración en clon y restauración probada. Los workers paralelos deben utilizar PostgreSQL; SQLite sirve para desarrollo aislado y no acredita bloqueo concurrente de filas.

## Comando por empresa

Estado de solo lectura por defecto, desde la raíz y con una instalación fresh-local previamente creada:

```bash
python BACKEND/deployment/fresh_manage.py --directory /ruta/instalacion-privada --service erp-tur accounting_project --tenant UUID_EMPRESA_CONTABLE
```

Para aplicar un lote, el operador del host debe habilitar expresamente `ACCOUNTING_LOCAL_PROJECTION_ENABLED=1` en la configuración privada del proceso y añadir:

```bash
python BACKEND/deployment/fresh_manage.py --directory /ruta/instalacion-privada --service erp-tur accounting_project --tenant UUID_EMPRESA_CONTABLE --apply --limit 50
```

La variable no se modifica por API ni se activa al arrancar la aplicación. El UUID es el de Tenant contable verificado, no el del prestador. El operador utiliza credenciales de base autorizadas para ese entorno; este comando no concede permisos de aplicación a empleados. Cada invocación procesa un lote de1–100 trabajos, sin daemon, cron ni bucle permanente habilitado automáticamente.

La salida omite saldos, credenciales y payloads: informa cantidades, estados y códigos acotados. Conservar los resultados operativos privados; no subir `.env`, bases, claves o registros de clientes a Git. Los errores de configuración/esquema no se convierten en ejecuciones exitosas.

## Máquina de estados

- **PENDING:** trabajo adoptado desde un evento contable v2, pendiente de intento.
- **LEASED:** reclamación con token opaco y plazo de60s, máximo5 intentos totales. El token no se incluye en API de estado ni salida del comando.
- **RETRY:** fallo transitorio; próxima fecha con espera exponencial acotada. El proceso no duerme bloqueando una transacción: una invocación posterior atiende trabajos vencidos.
- **DELIVERED:** proyección, recibo y confirmación local se confirmaron en una transacción.
- **QUARANTINED:** integridad/contrato inválidos, error inesperado o intentos agotados. No se reejecuta automáticamente; requiere investigar y reparar/revisar mediante un procedimiento futuro explícito.

Un trabajo expirado puede ser reclamado con token nuevo; el antiguo no puede confirmar ni afectar los saldos. Si se perdió una respuesta después de confirmar, el recibo único evita volver a sumar. Hay restricciones únicas por evento/consumidor y por asiento/consumidor.

El consumidor vuelve a comprobar contrato, empresa, hash del asiento, balance, moneda y snapshot del evento. Actualiza saldos diarios en moneda base, no el asiento original. Un error antes de confirmar revierte saldos, recibo y confirmación juntos.

## Consulta del titular

Ruta existente de contabilidad, nueva acción de lectura:

`GET /api/v1/mi-negocio/contable/contabilidad/cuentas/estado-proyeccion/?provider_id=UUID_PRESTADOR`

Usa la sesión/JWT, propiedad y VerifiedCompanyLink del módulo. Una persona ajena o un superusuario sin titularidad no accede por enviar encabezados. No permite iniciar el worker ni dar por publicado un evento.

Campos: estados agregados, últimas20 fallas/códigos, `failures_truncated`, asientos fuente, recibos, diferencia entre ambos y `complete`. Los saldos acumulados por cuenta/moneda solo aparecen cuando todo el universo comprobado tiene recibo, no hay trabajos pendientes/apartados y no existen asientos legados o saldos iniciales por conciliar. Si falta algo, `balances=[]` y `complete=false`; esa lista no significa saldo financiero cero.

Es una consulta operativa de la proyección acumulada, no un estado fiscal certificado ni un informe histórico por fecha. El reporte autorizado por fecha sigue en `cuentas/balance-prueba/`. La lectura de estado se serializa con el posteo y consumo de la misma empresa para evitar mezclar contadores y saldos de instantes distintos.

## Publicación externa y límites

`OutboxEvent.status` y `published_at` **no se modifican** al confirmar una proyección local. Un recibo local no prueba entrega a Kafka, DIAN, bancos, WebSocket o un cliente. El eventual adaptador externo tendrá su propio acuse, reintentos, deduplicación, permisos y prueba de broker. Los consumidores y productores legados siguen requiriendo migración de contrato/actor.

No hay limpieza automática, reconstrucción destructiva de proyecciones ni reutilización de recibos para otros consumidores. Faltan reconciliación/rebuild supervisados, retención, monitorización continua, despliegue del worker y medición de carga/latencia. Las guardas no sustituyen permisos SQL ni una firma/anclaje independiente ante un operador privilegiado.

Los controles de fondos de billetera y sus autorizaciones permanecen separados. Este consumidor de lectura derivada no autoriza transferencias, no liquida offline y no habilita nuevas acciones para el motor de escritorio.

## Verificación enfocada

`python INTEGRACIONES/operacion/verify_local.py --profile accounting --profile postgres --output /tmp/sgacd-proyeccion-evidencia-nueva` ejecuta únicamente los contratos contables y PostgreSQL. No certifica perfiles no seleccionados ni activa el worker del usuario.
