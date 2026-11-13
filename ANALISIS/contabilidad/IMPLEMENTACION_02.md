# Implementación02 · Posteo, identidad e informes del núcleo compartido

Estado: implementación local sobre el motor existente, con pruebas y migraciones aditivas preparadas. **No es cierre de los siete pools ni habilitación productiva.** No se hicieron commits, push ni cambios sobre bases del usuario en este corte.

## Cambios operativos

### Posteo contable y eventos

`LedgerEngine.post_entry` usa empresa explícita o contexto autenticado, actor activo y responsable del borrador, periodo/fecha/moneda compatibles y cuentas de la misma empresa/plan. No infiere un superusuario para la auditoría. Los borradores con fecha económica futura no se contabilizan anticipadamente.

Se bloquea la fila de Tenant antes de operar. Dentro del servicio, esta serialización protege incluso asientos con cuentas distintas y coordina guardas ORM de encabezados/líneas. El posteo, auditoría y `OutboxEvent` se confirman en una transacción SQL: falla cualquiera y se revierten los cambios. No se invoca el bus externo ni Kafka dentro de esa transacción.

`AccountingEventReceipt` tiene unicidad SQL por empresa/evento. Los reintentos del mismo contrato recuperan el mismo asiento; cambiar el payload, tipo o actor con la misma clave produce rechazo. Un evento legado sin recibo requiere conciliación antes de reproducirse: no se contabiliza dos veces ni se crea recibo ficticio.

El nuevo contrato de salida es `accounting.entry.posted.v2`, con importes decimales como texto, tenant, actor, id, hash y versión. Permanece **PENDING**; aún falta un publicador/consumidor real con reintentos y deduplicación. No se anuncia que exista Kafka operativo, exactamente una entrega distribuida o ACID entre servicios externos.

### Integridad y contrapartidas

Los nuevos asientos usan hash canónico `v2`: identidad, empresa, periodo, fecha, referencia/descripción, actor, moneda/tasa, evento/regla y líneas con cuentas, clasificación, importes y moneda base. `compute_hash`, el motor y el validador central utilizan el mismo contrato v2.

Los hashes antiguos se conservan con versión `legacy`; se pueden verificar los dos algoritmos históricos sin reescribirlos. Los nuevos asientos continúan la cadena anterior. No se genera la antigua cadena de texto que aparentaba una firma: `immutable_signature` queda sin firma en v2. **Un hash no es firma digital, Merkle, ZKP ni prueba emitida por un regulador.**

Las contrapartidas son asientos nuevos, mantienen el original y no se duplican. Se exige un periodo actual abierto y actor explícito. Las reversiones con diferencias de moneda requieren un flujo contable específico y se rechazan; no se inventan diferencias de cambio. Las guardas ORM no sustituyen restricciones/permisos contra SQL directo o usuarios privilegiados.

### FX y saldos

No hay tasa1.0 de respaldo para divisas diferentes. Se exige una tasa positiva registrada, marcada oficial, con monedas activas y fecha efectiva no posterior al hecho. La tasa aplicable queda en el asiento y su hash; se rechazan tasas manuales contradictorias y mezcla de monedas de transacción dentro del mismo asiento.

La conversión a base usa redondeo HALF_UP explícito; si la distribución produce descuadre, se requiere ajuste revisado, no una corrección silenciosa. Esta entrega no valida el proveedor real de TRM ni define automáticamente caducidad de feeds o política normativa para todas las monedas/activos.

Los reportes se calculan en moneda base a partir de líneas contabilizadas y ámbito empresarial explícito. El balance de prueba usa consultas agrupadas, hasta3 consultas en el caso medido, sin una consulta por cuenta. El estado de resultados incorpora costos; el balance incluye resultados en patrimonio. El flujo de caja que devolvía ajustes cero ficticios ahora responde como no implementado.

Si hay saldos iniciales almacenados fuera de asientos, los informes se bloquean hasta conciliar su apertura. Los valores no se borran ni se duplican automáticamente. Tampoco se presentan balances completos que omitan esas cantidades.

### Adaptación turística y API

`ContabilidadService.crear_asiento_completo` resuelve `VerifiedCompanyLink`: TourismProvider y Tenant son identificadores distintos. Verifica titular, vínculo, vigencia, actor, periodo y cuentas; la creación+posteo exige `idempotency_key`. No se hereda acceso por ser empleado o superusuario.

La API existente de cuentas usa JWT o sesión ERP/CSRF y la empresa verificada del titular. Encabezados y `request.tenant_id` no conceden propiedad. Se rechazan campos de saldo/tenant/tipo derivados del servidor, padres ajenos/cíclicos, reclasificación de cuentas ya contabilizadas y eliminación del catálogo histórico. Las actualizaciones se revalidan después del bloqueo.

Nueva consulta de solo lectura:

`GET /api/v1/mi-negocio/contable/contabilidad/cuentas/balance-prueba/?provider_id=<UUID_PRESTADOR>&fecha_corte=2026-11-08`

La ruta relativa del router es `cuentas/balance-prueba/`; comprobar el prefijo montado en la instalación. Importes de respuesta como texto decimal, moneda de la empresa y solo datos propios. No se añadió un endpoint que permita saltarse aprobaciones para pagos, billetera o ejecución de cuentas externas.

## Instalación y compatibilidad

- Fresh-local: `BACKEND/deployment/fresh_migrations/core_erp/0002_ledger_posting_v2.py`.
- Grafo original: `BACKEND/ANALEMATICA-BACKEND/core_erp/migrations/0002_ledger_posting_v2.py`.
- Añaden `hash_version` (default `legacy`) y tabla de recibos con restricción única; no rehacen saldos/hashes ni borran datos.
- Se probaron instalación nueva del ERP, esquema/readiness, migración repetible y once regresiones sobre esa base. El grafo histórico y su aplicación a bases existentes requieren preflight/restauración en una copia; no se han certificado ni migrado datos reales.
- Los productores legados deben proporcionar un actor confiable y un contrato estable. No se acepta un `user_id` arbitrario del payload como autorización. Adaptadores antiguos sin esos datos fallan; se retiró la captura que ocultaba el fallo en el handler contable estándar.
- El publicador v2, WebSockets/proyecciones antiguas y otros consumidores deben adaptarse antes de activar automatización. El estado PENDING de outbox no es confirmación de publicación ni acuse fiscal/bancario.

## Verificaciones y evidencia

Pruebas nuevas y ampliadas: `accounting_posting_check.py`, `accounting_adapter_check.py` y `accounting_postgres_contract.py`; las nueve pruebas originales de fundación siguen en su suite. Los tests de posteo también repiten esas nueve como regresión, por lo que el total ejecutado no representa casos únicos.

Casos PostgreSQL: mismo evento concurrente, payload divergente, cuentas disjuntas/cadena por empresa, reversión repetida, edición frente a posteo y cierre frente a posteo. Cada caso usa conexiones independientes en una base temporal aparte; se comprueban cadena, número de asientos y outbox. No es un benchmark de producción o una prueba de fallo entre centros de datos.

Las pruebas API usan identidad forzada de fixture; las regresiones generales validan por separado sesiones/autenticación. No se certifica aquí una experiencia web contable completa, navegadores reales de todo el módulo ni el objetivo250ms. Los builds web anteriores continúan pendientes.

## Próximos pasos de la matriz

Publicador v2 y consumidores; migración de productores antiguos con identidad y reglas revisadas; flujo de aprobación/manual contable en interfaz; apertura y conciliación de saldos; reversión multimoneda y fuente/frescura de tasas; restricciones SQL y revisión independiente de integridad; impuestos/DIAN, bóveda cliente BYOS, nómina/SG-SST, ratios turísticos, Eco-Ledger y consultas IA limitadas.

La billetera mantiene sus autorizaciones y registro de pendientes propios; este cambio del libro mayor no habilita fondos externos ni liquidación offline.

## Resultado final de este corte

- **18 grupos seleccionados aprobados**, con254 métodos de prueba Python ejecutados. Incluyen23 de posteo (9 reutilizan fundación) y8 del adaptador/API.
- **27 escenarios PostgreSQL aprobados**:21 previos y6 contables nuevos, sobre una base temporal independiente. No se usaron bases reales ni se enviaron eventos a proveedores.
- **11 regresiones de instalación nueva ERP aprobadas**: esquema listo, migración repetible, ausencia de drift y recorridos existentes. El grafo nativo se entrega preparado, sin afirmar aplicación validada a una base histórica.
- Fuente seleccionada estable y hashes del paquete de evidencias verificados. Código de salida0 para los perfiles `core + postgres`; esto no revalida builds web o dispositivos físicos pendientes.

Resumen persistente: `evidencias/implementacion-02.json`; informe de grupos: `evidencias/implementacion-02-verificacion.json`. Registros privados originales en `/tmp/sgacd-accounting-release-38`; no se copian claves, bases ni registros completos al repositorio. El resumen público no permite verificar archivos privados que no se incluyeron.

```bash
python BACKEND/deployment/tests/accounting_posting_check.py -v
python BACKEND/deployment/tests/accounting_adapter_check.py -v
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile core --profile postgres --output /tmp/sgacd-contabilidad-evidencia-nueva
```

No hubo cambios de diseño visual. Las automatizaciones y funciones todavía no implementadas permanecen en la matriz; no se declara el módulo completo al100%.
