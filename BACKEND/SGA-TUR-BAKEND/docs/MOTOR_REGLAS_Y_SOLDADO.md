# MOTOR DE REGLAS Y SOLDADO LEDGER WRITER — SARITA 2026

## 🧠 Bloque 5: Posting Rules Engine (Determinismo)

El motor traduce el evento comercial en asientos de doble partida basándose en reglas pre-configuradas por tipo de negocio y país:

| Escenario | Débito | Crédito | Impuesto |
| :--- | :--- | :--- | :--- |
| **Hospedaje** | 1305 (CxC) | 4135 (Serv. Hotel) | 2408 (IVA 19%) |
| **Restaurante** | 1105 (Caja) | 4135 (Alimentos) | 2805 (Impoconsumo) |
| **Agencia** | 1305 (CxC) | 4135 (Comisión) | 2408 (IVA 19%) |

## 👷 Bloque 6: Soldado LedgerWriter (N6 Oro)

Este soldado es el ejecutor atómico final. Su única misión es la persistencia íntegra.

### Responsabilidades:
1.  **Validar Periodo Abierto:** `if period.status == 'CLOSED' raise PeriodClosedError`.
2.  **Validación Multi-tenant:** Filtro estricto por `tenant_id`.
3.  **Escritura Atómica:** `with transaction.atomic()` para `JournalEntry` y `JournalLines`.
4.  **Validación de Balance:** `if sum(debits) != sum(credits) raise UnbalancedError`.
5.  **Cierre:** Registrar en `ProcessedEvents` y `OutboxEvent`.

---
**Resultado:** La contabilidad deja de ser una decisión de la IA para convertirse en un reflejo exacto y matemático de la realidad comercial.
