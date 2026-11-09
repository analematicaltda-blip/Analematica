# Conciliación parcial de filas importadas

Se conserva el CSV neutral y el límite de30 filas por revisión. La comparación devuelve candidatos por la misma cuenta/empresa/fecha/dirección/importe. No se aplican tolerancias, FX ni cuentas puente implícitas. El CSV y las referencias originales no se persisten; se conservan sus huellas y los metadatos revisados.

## Uso en ambos paneles

1. Cargar cuentas revisadas, seleccionar cuenta y cargar CSV local.
2. Comparar. Cada fila permite elegir candidato o motivo pendiente. Una coincidencia única se presenta preseleccionada, pero todavía requiere las dos autorizaciones.
3. Las filas ambiguas requieren selección explícita; las filas sin coincidencia requieren motivo. Debe existir al menos una coincidencia real. No es posible registrar todas las filas como diferencias y llamarlas conciliación.
4. Completar evidencia y primera confirmación; revisar coincidencias/diferencias persistidas.
5. Segunda autorización para registrar las asociaciones. Una diferencia pendiente mantiene el resultado parcial.
6. Recuperar sin restaurar autorizaciones. Para corregir: revisión y confirmación de liberación, comparar nuevamente, resolver y volver a revisar. El historial se conserva.

Motivos admitidos: `BANK_FEE_UNPOSTED` (cargo pendiente de contabilizar), `TIMING_DIFFERENCE` (diferencia temporal), `UNIDENTIFIED` (sin identificar) y `REQUIRES_ADJUSTMENT` (requiere ajuste revisado). Un motivo es una declaración respaldada del propietario, no una validación profesional ni un ajuste contable.

## Contrato compatible

`review_bank_reconciliation` admite opcionalmente `resolutions`, con un objeto por fila: `row` entero, `ledger_line_id` UUID canónico o nulo y `reason_code` nulo o motivo admitido. No se pueden repetir filas o líneas contables. Una referencia pendiente también queda reservada hasta liberar su conciliación.

Sin `resolutions`, el contrato anterior sigue exigiendo coincidencia única para todas las filas. Con resoluciones, la instantánea contiene `rows`, `differences` y `coverage`: conteos y totales separados de entradas/salidas asociadas y pendientes.

La confirmación devuelve `associations_confirmed` para las asociaciones vigentes. `fully_reconciled` y `reconciliation_confirmed` solo son verdaderos cuando todas las filas importadas tienen asociación vigente. No significan conciliación del saldo de la cuenta o del período completo. Reversión/integridad inválida revocan la calificación vigente; liberación la desactiva sin borrar evidencia.

El puente corporativo comprueba que las decisiones y totales devueltos coincidan con la solicitud y que un estado parcial o liberado no se anuncie como completo. Solo permite el origen fijo del ERP, sesión/CSRF y vínculo empresarial vigentes.

## Versiones y operación segura

Las resoluciones explícitas producen revisión/confirmaciónv2. Se conservan reservas compatibles cuyo origen requiere lectorv2: un serviciov1 no puede reutilizar una referencia confirmada de estos registros. Los lectores nuevos recuperan ambos formatos históricos. Antes de un despliegue o reversión, probar lectores/colas/informes con ambas versiones; no operar el flujo parcial con una versión antigua.

El modo actual no divide el importe de una fila entre varios asientos ni vincula varias filas con partes del mismo asiento. No genera gastos por comisiones, ajustes bancarios ni pagos; deben existir sus procesos contables revisados separados.
