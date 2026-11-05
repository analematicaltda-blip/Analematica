# ALGORITMOS ANALÍTICOS DETERMINÍSTICOS — SARITA 2026

## 🎯 Objetivo (Bloque 5, 6, 7 y 8)
Establecer las fórmulas matemáticas inalterables que rigen la Torre de Control. Se prohíbe el uso de heurísticas no auditables.

## 📊 1. ROI (Return on Investment)
- **Fórmula:** `(Utilidad Neta / Inversión Total) * 100`.
- **Fuente:**
    - `Utilidad Neta` = Cuentas de Ingresos (4) - Gastos (5) - Costos (6) del `LedgerEngine`.
    - `Inversión Total` = Activos fijos y capital de trabajo registrado en el balance.

## 👥 2. LTV (Lifetime Value)
- **Fórmula Avanzada:** `ARPU / ChurnRate`.
- **Cálculo:**
    - `ARPU` (Average Revenue Per User) = Suma Facturado Mensual / Clientes Activos.
    - `ChurnRate` = Clientes perdidos en los últimos 30 días / Clientes activos al inicio del periodo.

## 📉 3. Churn (Tasa de Deserción)
- **Definición de Cliente Perdido:** Suscripción marcada como `CANCELLED` o Inactividad Operativa > 45 días detectada por el `SADI Agent`.
- **Cálculo de Cohorte:** Solo se consideran clientes con al menos 1 factura pagada en el ciclo anterior.

## 🔮 4. Forecast (Proyección Predictiva)
- **Modelo:** Promedio Móvil Ponderado (WMA) de 6 meses.
- **Ponderación:** Los últimos 2 meses tienen un peso del 60% en la proyección.
- **Validación:** Se mostrará un `ConfidenceScore` basado en la desviación estándar histórica del Tenant.

---
**Regla de Integridad:** Ningún KPI se mostrará en la UI si el periodo contable no ha pasado el chequeo de "Balance de Prueba" (`assets == liabilities + equity`).
