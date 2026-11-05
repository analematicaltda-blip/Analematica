# ARQUITECTURA DE API CONTABLE — SARITA 2026

## 🎯 Objetivo (Bloque 3 y 4)
Centralizar la exposición de todos los servicios financieros bajo una estructura de API limpia, jerárquica y segura. El frontend dejará de llamar a microservicios dispersos para usar el Hub Contable central.

## 🚀 Mapeo de Endpoints (Hub Contable)

| Módulo | Endpoint | Propósito |
| :--- | :--- | :--- |
| **Plan de Cuentas** | `GET /api/contabilidad/cuentas` | Catálogo completo con jerarquía IFRS. |
| **Libro Diario** | `GET /api/contabilidad/asientos`| Registro cronológico de transacciones. |
| **Balance** | `GET /api/contabilidad/balance` | Situación financiera (Assets, Liab, Equity). |
| **Resultados** | `GET /api/contabilidad/pnl` | Estado de pérdidas y ganancias (Income/Exp). |
| **Libro Mayor** | `GET /api/contabilidad/ledger` | Movimientos detallados por cuenta específica. |
| **Cash Flow** | `GET /api/contabilidad/cashflow`| Flujo operativo, inversión y financiación. |
| **Consolidado** | `GET /api/contabilidad/holding` | Balance multi-tenant del grupo corporativo. |
| **Acciones** | `POST /api/contabilidad/reverse` | Generación de asientos de anulación. |

## 🏗️ Estructura de Respuesta Determinística

Para evitar cálculos en el frontend (Bloque 9), toda respuesta de reporte debe seguir este esquema:

```json
{
  "period": "2026-03",
  "currency": "COP",
  "tenant_id": "UUID",
  "totals": {
    "debit": 15000000.00,
    "credit": 15000000.00,
    "net": 0.00
  },
  "data": [
    { "code": "1105", "name": "Caja", "balance": 500000.00, "percentage": 3.3 }
  ],
  "traceability": {
    "snapshot_id": "UUID",
    "signature": "SHA256-HASH"
  }
}
```

---
**Regla de Oro:** Ninguna vista del Dashboard de "Mi Negocio" podrá realizar operaciones `SUM` o `Filter` sobre el estado financiero del lado cliente. El Backend entrega la verdad masticada.
