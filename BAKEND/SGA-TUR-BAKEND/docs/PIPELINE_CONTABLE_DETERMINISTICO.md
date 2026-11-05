# PIPELINE DETERMINÍSTICO: VENTAS → CONTABILIDAD — SARITA 2026

## 🎯 Objetivo (Bloque B)
Eliminar el cableado manual y garantizar que cada venta confirmada impacte el Ledger de forma automática, irreversible e idempotente.

## 🏗️ Esquema de la Tabla `ProcessedEvents`

Para garantizar la **Idempotencia (Bloque B.3)**, se implementará el siguiente modelo:

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `event_id` | UUID | ID único del evento raíz (`SALE_CONFIRMED`). |
| `processed_at` | DateTime | Timestamp de la ejecución exitosa. |
| `status` | Enum | SUCCESS, FAILED. |
| `target_entity_id`| UUID | ID del `JournalEntry` creado. |

## 🔄 El Ciclo de Vida Determinístico

1.  **Emisión:** El dominio `comercial` emite `SALE_CONFIRMED`.
2.  **Filtrado:** El `AccountingSubscriber` consulta `ProcessedEvents`. Si existe `status=SUCCESS`, ignora el evento.
3.  **Regla:** El `PostingRulesEngine` mapea la venta según la configuración fiscal activa.
4.  **Acción:** El `SoldadoLedgerWriter` (N6 Oro) ejecuta en `transaction.atomic()`.
5.  **Reversión:** Si se emite `SALE_REVERSED`, el suscriptor busca el `target_entity_id` original y dispara la misión `REVERSE_ENTRY`.

## 🛡️ Reglas de Reversión Automática (Bloque B.4)
- No se permite borrar asientos.
- La anulación de una factura genera un asiento con montos invertidos (Débito <-> Crédito).
- El nuevo asiento debe estar vinculado al `correlation_id` original.

---
**Resultado Esperado:** 0% de ventas sin asiento contable asociado en producción masiva.
