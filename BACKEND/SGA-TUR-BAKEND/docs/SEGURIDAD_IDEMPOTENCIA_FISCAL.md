# SEGURIDAD E IDEMPOTENCIA FISCAL — SARITA 2026

## 🆔 Bloque 10: Idempotencia en Cálculos
Para evitar que un documento genere múltiples transacciones fiscales ante fallos de conexión:

1.  **Hash de Cálculo:** Cada `TaxTransaction` guardará un `calculation_hash = SHA256(doc_id + version + base_amount)`.
2.  **Validación:** Antes de registrar un nuevo impuesto, el `TaxEngine` verifica la existencia del hash. Si existe, ignora el cálculo repetido.

## ↩️ Bloque 11: Reversión Controlada Inmutable

Queda prohibido el uso de `DELETE` en el dominio fiscal.

- **Escenario:** Factura Anulada.
- **Acción:**
    1.  El sistema busca la `TaxTransaction` original.
    2.  Genera una nueva transacción con el monto en negativo (ej: -$19,000).
    3.  Referencia al documento de anulación (`CreditNote`).
    4.  Impacta la contabilidad con un asiento de reversión inmutable.

## 🔒 Bloque 12: Auditoría Forense Fiscal
Cada cambio en la configuración de tasas (`TaxRule`) registrará:
- **Actor:** Usuario que realizó el cambio.
- **Timestamp:** UTC exacto.
- **Rastro:** Valor anterior vs Valor nuevo.
- **Sello:** Hash de integridad que vincula el cambio con la resolución legal adjunta.

---
**Resultado:** Trazabilidad extrema. Un auditor puede reconstruir la cadena: Venta -> Cálculo IA -> Regla Fiscal -> Asiento Ledger.
