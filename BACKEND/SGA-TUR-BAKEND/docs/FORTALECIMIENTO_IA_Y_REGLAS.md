# FORTALECIMIENTO DE IA Y REGLAS CONTABLES — SARITA 2026

## 🛰️ Bloque 18: Integración General SADI Backend

El Agente SADI deja de ser un motor de chat para ser un **Motor Transversal de Decisión**.

1.  **Ingesta Contextual:** SADI recibe los estados del Ledger y del Motor Comercial en tiempo real.
2.  **Jerarquía N1-N6:** SADI no puede ejecutar ORM directamente. Emite **Recomendaciones Estructuradas** al General (N1), quien autoriza la delegación de la misión.
3.  **Evento de Decisión:** Cada vez que SADI propone un cambio (ej: ajuste de precios), se emite el evento `STRATEGIC_PROPOSAL_GENERATED`.

## 🔒 Bloque 20: Endurecimiento de Posting Rules (Hard Check)

Antes de que cualquier "Soldado de Oro" pueda escribir un asiento, el motor de reglas debe pasar estas 4 validaciones críticas:

1.  **Periodo Abierto:** `period.status == 'OPEN'`.
2.  **Validación de Régimen:** El `TaxEngine` confirma que el IVA/Retención aplicado corresponde al régimen fiscal del Tenant.
3.  **Coherencia de Partida Doble:** `if sum(debits) != sum(credits) raise UnbalancedAccountingEntryError`.
4.  **Jurisdicción Fiscal:** Validación de que la regla de impuesto pertenece al país de operación declarado en el Tenant.

---
**Resultado:** Una IA gobernada por leyes financieras inmutables y un motor contable blindado contra errores de cálculo.
