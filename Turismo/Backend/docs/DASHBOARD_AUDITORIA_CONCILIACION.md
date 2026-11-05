# DASHBOARD Y AUDITORÍA DE CONCILIACIÓN — SARITA 2026

## 📊 Bloque 7: Panel de Control Financiero (Vía 1 y 2)

La interfaz mostrará indicadores de salud bancaria en tiempo real:

- **% Conciliación Automática:** Meta >= 85%. Refleja la eficiencia del motor de matching.
- **Exposure Gap:** Suma de montos en `EXCEPCIÓN` (Riesgo de liquidez no identificada).
- **Time to Reconcile:** Tiempo promedio entre la operación bancaria y el match contable (Target < 24h).
- **Audit Health:** Estado de la cadena de hashes SHA-256 de las conciliaciones.

## 📝 Bloque 6: Motor de Auditoría Financiera

Cada acción dentro del motor de conciliación generará una bitácora inmutable:

| Nivel | Evento | Metadatos Obligatorios |
| :--- | :--- | :--- |
| **INFO** | `SYNC_STARTED` | `source_ip`, `request_id`. |
| **INFO** | `AUTO_MATCH` | `banco_id`, `wallet_tx_id`, `logic_used`. |
| **WARNING** | `MANUAL_ADJUST` | `user_id`, `justification`, `before_after_delta`. |
| **CRITICAL**| `MATCH_DELETED` | `audit_ref`, `sovereign_auth_code`. |

---
**Garantía de Cierre:** El sistema bloqueará el "Cierre Mensual" si el % de conciliación es inferior al 100% (todas las excepciones deben ser resueltas o marcadas como reclamo oficial).
