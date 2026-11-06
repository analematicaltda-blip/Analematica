# MATRIZ DE CERTIFICACIÓN DE SINCRONIZACIÓN — SARITA 2026

## 🧪 Bloque 12: Pruebas Obligatorias de Integridad

El sistema debe superar el 100% de estos escenarios antes del cierre definitivo:

| Test ID | Escenario | Resultado Esperado |
| :--- | :--- | :--- |
| **TS-01** | Venta Nacional IVA 19% | Asiento generado con desglose de cuenta 2408. |
| **TS-02** | Evento Duplicado | Cero creación de segundo asiento (Idempotencia). |
| **TS-03** | Anulación de Factura | Generación de asiento inverso vinculado. |
| **TS-04** | Periodo Cerrado | Lanzamiento de `PeriodClosedError` (No escritura). |
| **TS-05** | Multi-Tenant Breach | El Tenant A no puede consultar asientos del Tenant B. |
| **TS-06** | Venta Multimoneda | Registro en COP y USD con tasa de cambio histórica. |
| **TS-07** | Stress (10k tx) | Consistencia 100% en el balance del Ledger. |

## ✅ Bloque 14: Condición de Producción Masiva

SARITA se declara lista para la producción cuando los indicadores de salud en la Torre de Control marquen:
- **Sincronización:** 100% (Ventas sin asiento = 0).
- **Integridad:** 100% (Cadena de hashes SHA-256 válida).
- **Outbox Latency:** < 500ms promedio.

---
**Aval Final:** Con este pipeline, la contabilidad deja de ser un problema administrativo para convertirse en una ventaja competitiva de tiempo real.
