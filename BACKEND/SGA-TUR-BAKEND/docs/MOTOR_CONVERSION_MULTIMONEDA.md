# MOTOR DE CONVERSIÓN MULTIMONEDA (FX ENGINE) — SARITA 2026

## 🎯 Objetivo (Bloque 9)
Convertir los estados financieros locales (COP, MXN, EUR) a la moneda base del Holding (ej: USD) garantizando la trazabilidad de la tasa de cambio utilizada y el cumplimiento de las NIIF (IFRS).

## 🔄 9.1 Reglas de Conversión Determinísticas

El motor aplicará diferentes tipos de tasa según la naturaleza de la cuenta:

| Naturaleza | Tasa Aplicable | Justificación Contable |
| :--- | :--- | :--- |
| **Balance (Activos/Pasivos)** | **Tasa de Cierre** | Valor de liquidación al día del reporte. |
| **Resultados (Ingresos/Gastos)**| **Tasa Promedio** | Refleja la operación acumulada del periodo. |
| **Patrimonio** | **Tasa Histórica** | Mantiene el valor original de los aportes. |

## ⚙️ 9.2 El Flujo FX

1.  **Consulta de FXRateTable:** El motor busca la tasa oficial configurada para el par `Currency_Local/Currency_Base` en el periodo específico.
2.  **Cálculo de Diferencia en Conversión:** Debido al uso de diferentes tasas, el Balance puede no cuadrar. El sistema generará automáticamente la cuenta de **Ajuste por Diferencia en Cambio (Patrimonio)** para balancear el snapshot.
3.  **Persistencia:** La tasa de cambio utilizada se guarda en el metadata del `ConsolidatedReportSnapshot` para auditoría externa.

---
**Regla de Seguridad:** Ninguna consolidación puede realizarse utilizando tasas de cambio "vivas" de internet sin previa validación y firma por parte del Controller Corporativo.
