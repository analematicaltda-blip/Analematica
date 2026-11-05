# MOTOR DE CONCILIACIÓN BANCARIA (RECONCILIATION ENGINE) — SARITA 2026

## 🎯 Objetivo (Bloque 2)
Implementar el motor inteligente encargado de cruzar la "Verdad Externa" (Monedero Soberano/Bancos) con la "Verdad Interna" (Libro Mayor/Wallet).

## 🏗️ Modelos de Datos de Conciliación

### 1. `BancoTransaction` (Extracto)
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `referencia` | Char(255)| ID externo de la operación. |
| `monto` | Decimal | Valor real recibido/enviado. |
| `fecha_operacion`| Date | Fecha según el banco/monedero. |
| `estado` | Enum | PENDING, RECONCILED, EXCEPTION. |

### 2. `Conciliacion` (El Match)
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `banco_id` | FK | Referencia a la transacción externa. |
| `wallet_tx_id` | UUID | Referencia a la transacción interna. |
| `match_type` | Enum | EXACT, PARTIAL, MANUAL. |
| `diff_amount` | Decimal | Diferencia detectada (Tolerancia). |

## 🧠 Lógica de Matching Inteligente

El motor ejecutará un pipeline de búsqueda en cascada:

1.  **Nivel 1 (Exacto):** `monto == monto` AND `referencia == referencia` AND `abs(días) <= 1`.
2.  **Nivel 2 (Referencia Parcial):** `referencia` externa contenida en el campo `metadata` interno.
3.  **Nivel 3 (Agrupado):** Suma de N transacciones internas que igualan a una transacción bancaria (ej: liquidación masiva).

---
**Regla de Seguridad:** Ninguna transacción marcada como `RECONCILED` puede ser modificada en el Ledger sin romper la firma de la conciliación.
