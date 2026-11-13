# Implementación03 · Entrega local y proyección contable idempotente

Continuación del núcleo compartido de Analemática y ERP turístico. Estado: implementado en desarrollo y probado en aislamiento; no producción, no broker externo y sin commits/push de este corte.

## Qué cambia

1. Consumidor local optativo para `accounting.entry.posted.v2`. Solo procesa eventos y asientos de la empresa seleccionada; vuelve a validar contrato, identidad de asiento, hash y balance antes de afectar proyecciones.
2. Trabajos persistentes con plazo de ejecución, token, intentos, fechas y códigos de fallo. Reclamación concurrente PostgreSQL, recuperación de plazos vencidos y rechazo del token anterior.
3. Recibos únicos por evento y asiento/consumidor. La actualización de saldos diarios, el recibo y la confirmación se realizan en una misma transacción. Una repetición no duplica importes; una contrapartida añade su efecto sin borrar el original.
4. Reintentos transitorios acotados y separación de fallos de integridad. Máximo5 intentos; el agotamiento y los trabajos inválidos quedan apartados para revisión. No se guardan excepciones completas, tokens ni payloads en el código de fallo.
5. Comando `accounting_project` de solo lectura por defecto. Requiere feature flag y `--apply` para procesar un lote; no se programó ningún worker sobre datos reales.
6. Consulta de estado para el titular, dentro del API contable existente, con sus permisos y vínculo empresarial. Si la proyección no está completa o hay apertura/historia pendiente, no devuelve cantidades como si fueran un balance completo.
7. Confirmación local separada de publicación externa: los campos del outbox original que indican publicación permanecen intactos.

Código nuevo en `core_erp/accounting/delivery.py` y `delivery_models.py`; tablas aditivas en `core_erp.0003_accounting_projection`. Se conserva el ledger, no se reemplaza ni se reescribe su historia. [Operación y contratos](OPERACION_PROYECCIONES.md).

## Evidencia y alcance

Los casos locales comprueban: flujo exitoso, feature flag apagada, comando read-only sin escrituras, expiración y token incorrecto, reejecución con recibo, rollback, alteración de evento/asiento, backoff y agotamiento, ámbito empresarial, apertura/historia pendientes y contrapartidas.

Los casos PostgreSQL añadidos cubren: dos reclamaciones sobre un trabajo; consumo duplicado; eventos paralelos que actualizan el mismo saldo; token antiguo frente a uno renovado; repetición con recibo ya confirmado; fallo y recuperación transaccional. Se ejecutan en una base temporal separada de las pruebas MFA y del usuario.

La migración se verificó en el fresh-local de ERP, con las once regresiones existentes y sin drift. No se aplicó el grafo nativo a una base histórica ni se tocaron datos del usuario. Las pruebas de API usan identidad de fixture y no certifican un recorrido web completo.

## Límites que siguen abiertos

- Kafka/publicación externa y sus acuses: no implementados por este consumidor local.
- Integración continua de productores, reprogramación del worker, reconciliación/rebuild supervisados y retención.
- Medición del objetivo250ms, carga, fallos de infraestructura y revisión SQL/criptográfica independiente.
- Bóveda BYOS, DIAN, SG-SST/nómina, ratios turísticos, Eco-Ledger y asistentes financieros supervisados de los demás pools.
- Los builds web y equipos físicos pendientes del plan anterior no se cierran con estas pruebas.

No se modificó el diseño visual ni se habilitaron pagos o automatizaciones sobre cuentas reales. Los análisis y evidencia quedan en esta carpeta; no se crean informes sueltos en la raíz.

## Resultado de verificación

- **55 métodos contables** en el perfil enfocado:9 fundación,23 posteo,9 adaptador/API y14 entrega. La suite de posteo repite9 métodos de fundación; el total no es un conteo de casos únicos.
- **33 escenarios PostgreSQL** aprobados:21 previos y12 contables, de los cuales6 comprueban la entrega/proyección. Conexiones independientes, base temporal separada y sin efectos duplicados en los casos medidos.
- **11 pruebas de ERP migrado** y su readiness/drift pasaron con `0003_accounting_projection`; solo base temporal.
- **269 métodos en la regresión general** de esta fase y14 del verificador aprobados. La regresión general precede los ajustes finales de timestamps de diagnóstico/tokens inválidos; el perfil enfocado valida la fuente actual.
- Perfiles finales `accounting + postgres`:5 grupos aprobados, fuente seleccionada estable, hashes verificados y salida0. No equivale a validar perfiles web/hardware pendientes.

Resumen: `evidencias/implementacion-03.json`; informe de grupos: `evidencias/implementacion-03-verificacion.json`. Evidencia privada en `/tmp/sgacd-accounting-final-scope-39`; no se copiaron claves, bases ni registros completos al repositorio. El paquete público resumido no contiene todos los registros privados necesarios para `--verify`.

```bash
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile accounting --profile postgres --output /tmp/sgacd-contabilidad-nueva
python BACKEND/INTEGRACIONES/operacion/verify_local.py --verify /tmp/sgacd-contabilidad-nueva
```
