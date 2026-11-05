# PIPELINE CONTABLE IRREVERSIBLE: VENTAS → LEDGER — SARITA 2026

## 🎯 Objetivo (Bloque 2)
Garantizar que cada venta confirmada impacte el Libro Mayor de forma automática, atómica y determinística. La contabilidad ya no es reactiva, es una consecuencia inmediata de la operación comercial.

## 🔄 El Flujo Determinístico Oficial

1.  **Venta Confirmada:** El módulo comercial dispara el evento raíz.
2.  **AccountingSubscriber:** Intercepta el evento y valida la idempotencia.
3.  **PostingRulesEngine:** Traduce el `sale_type` y `payment_method` en cuentas contables (1xxx, 4xxx, 2xxx).
4.  **SoldadoLedgerWriter (N6 Oro):** Ejecuta la escritura en el `LedgerEngine` central.
5.  **Audit & Outbox:** Se sella el asiento con SHA-256 y se registra el evento de salida.

## 📜 Estructura Obligatoria del Evento `SALE_CONFIRMED`

Cualquier evento de venta que no cumpla con este esquema será rechazado por el `EventBus`:

```json
{
  "event_id": "UUID-V4",
  "event_name": "SALE_CONFIRMED",
  "tenant_id": "UUID",
  "sale_id": "UUID",
  "customer_id": "UUID",
  "total": 125000.00,
  "currency": "COP",
  "tax_breakdown": [
    {
      "type": "IVA",
      "rate": 0.19,
      "amount": 19958.00
    }
  ],
  "sale_type": "HOTEL_SERVICE | RESTAURANT | TOUR_AGENCY",
  "payment_method": "CREDIT | WALLET | CASH",
  "correlation_id": "UUID",
  "timestamp": "ISO-8601",
  "schema_version": 1
}
```

---
**Resultado:** Cero ambigüedad en la recepción de datos comerciales por parte del sistema financiero.
