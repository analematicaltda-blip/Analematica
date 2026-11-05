# API UNIFICADA DE LA TORRE DE CONTROL — SARITA 2026

## 🎯 Objetivo (Bloque 9)
Centralizar el acceso a las métricas estratégicas mediante un único punto de entrada determinístico, garantizando que el frontend siempre visualice la "Verdad Financiera Única".

## 🚀 Endpoint Oficial

| Método | Endpoint | Acción |
| :--- | :--- | :--- |
| `GET` | `/api/kpis/control-tower` | Recupera el snapshot estratégico más reciente. |

### 🏗️ Estructura de Respuesta (JSON)
```json
{
  "timestamp": "2026-03-31T12:00:00Z",
  "status": "CALCULATED",
  "methodology_version": "v2.1-SOVEREIGN",
  "kpis": {
    "roi": {
      "value": 3.45,
      "unit": "X",
      "trend": "+0.15",
      "confidence": 0.98
    },
    "ltv": {
      "value": 1250.00,
      "unit": "USD",
      "trend": "+50.00",
      "cohort": "Q1-2026"
    },
    "churn": {
      "value": 0.012,
      "unit": "PERCENTAGE",
      "period": "ROLLING_30_DAYS"
    },
    "forecast": {
      "value": 150000.00,
      "unit": "USD",
      "target_date": "2026-06-30",
      "error_margin": 0.05
    }
  },
  "signature": "SHA256-KPI-SNAPSHOT-HASH"
}
```

## 🔒 Reglas de Consumo
1.  **Firma de Integridad:** El campo `signature` garantiza que los datos no fueron alterados en tránsito.
2.  **Versioning:** Cualquier cambio en la fórmula de ROI o LTV debe reflejarse en el campo `methodology_version`.
3.  **Caching:** El frontend debe cachear la respuesta por un máximo de 15 minutos, salvo invalidación manual.

---
**Resultado:** Cero discrepancia entre la Torre de Control y el balance auditado del ERP.
