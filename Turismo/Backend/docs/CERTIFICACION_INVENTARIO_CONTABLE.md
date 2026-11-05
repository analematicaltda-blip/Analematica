# MATRIZ DE CERTIFICACIÓN INVENTARIO-CONTABLE — SARITA 2026

## 🧪 Bloque X: Batería de Pruebas de Estrés y Consistencia

El sistema debe superar el 100% de estos escenarios para obtener la certificación **SOVEREIGN-INV**:

| Test ID | Escenario | Resultado Esperado |
| :--- | :--- | :--- |
| **TI-01** | Venta sin stock | Bloqueo de salida y error `InsuficientStock`. |
| **TI-02** | Entrada sin cuenta | Bloqueo de registro y error `AccountingParameterError`. |
| **TI-03** | Rollback contable | Si el asiento falla, el stock físico no debe alterarse. |
| **TI-04** | Transferencia multialmacén | Movimiento de stock en Kardex y reclasificación en Mayor. |
| **TI-05** | Revalorización masiva | Actualización de costo promedio y asiento de ajuste automático. |

## 📊 Bloque XI: Indicadores de Salud Sistémica (Torre de Control)

Se monitorearán en tiempo real:
- `% Sincronización Automática:` Target 100%.
- `Descuadre Kardex-Ledger:` Valor monetario de la diferencia (Target $0.00).
- `Productos sin Mapeo:` Conteo de SKUs que bloquean la operación.

---
**Aval Final:** Con la implementación de esta directriz, Sarita elimina los "Ajustes Manuales de Fin de Mes", permitiendo auditorías externas instantáneas y precisas.
