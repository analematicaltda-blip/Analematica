# Cotejo de período bancario declarado

El comando existente `review_bank_reconciliation` admite opcionalmente `period`, junto con las resoluciones de filas existentes o las coincidencias únicas del contrato histórico.

Campos exactos: `since`, `until` (fechas ISO), `opening`, `closing` (saldos firmados canónicos con dos decimales), `statement_complete: true` y `evidence_digest` (SHA256 del soporte legítimo conservado por el propietario). No admite coma flotante, ceros negativos ni saldos inferidos. El período debe estar cerrado, no ser futuro, contener todas las filas importadas y abarcar hasta367 días inclusivos.

## Operación en ambos paneles

1. Cargar cuentas y CSV; comparar y resolver cada fila.
2. Activar **Revisar saldos de un período completo**. Declarar fechas, saldo inicial, saldo final y huella; confirmar que el archivo incluye todo el período del extracto.
3. Primera autorización/revisión: comprobar saldos del banco y del libro, diferencias y movimientos contables sin asociación.
4. Segunda autorización: registrar las asociaciones y el cotejo. Si quedan diferencias, la interfaz no presenta el período como conciliado.
5. Recuperar sin restaurar autorizaciones. Si cambió el libro, liberar con dos autorizaciones y revisar nuevamente, conservando historia.

## Contrato de resultado

`period_assessment` contiene términos, saldos/entradas/salidas de banco y libro, diferencias de apertura/cierre/flujo, identificadores contables sin asociación, conteos y huella de historia contable. Su calificación exige diferencias cero, ninguna fila bancaria pendiente y ningún movimiento contable omitido. Igualdad de saldos por sí sola no basta.

`period_source_current` indica si el libro/clasificación siguen coincidiendo con la revisión. `period_reconciled` exige asociaciones vigentes, evaluación apta y fuente vigente. `period_requires_review` señala que una fuente de período activa cambió. Sin solicitud de período, la evaluación y vigencia son nulas y la conciliación de período es falsa. Los indicadores históricos de filas (`fully_reconciled`/`reconciliation_confirmed`) conservan su alcance de filas importadas.

Los importes y diferencias se calculan con centavos enteros, incluyendo saldos negativos. Se verifica la integridad de los asientos de caja y su valoración COP; no se aplica tasa FX implícita. Los movimientos posteriores al cierre no alteran el corte; movimientos retroactivos anteriores al corte sí invalidan su huella.

La declaración de archivo completo no prueba su autenticidad bancaria. `bank_verified` y `source_independently_verified` permanecen falsos. La captura conserva metadatos/huellas, no CSV ni referencias bancarias originales. No contabiliza comisiones, diferencias ni pagos automáticamente.
