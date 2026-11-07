# API DEL MOTOR DE CONCILIACIÓN — SARITA 2026

## 🎯 Objetivo (Bloque 4)
Exponer los servicios de conciliación para su consumo desde la Torre de Control y el Dashboard del Prestador (Vía 2).

## 🚀 Endpoints de Conciliación

| Método | Endpoint | Acción |
| :--- | :--- | :--- |
| `POST` | `/api/conciliacion/sync` | Dispara la descarga desde el Monedero Soberano. |
| `POST` | `/api/conciliacion/run` | Ejecuta el algoritmo de matching automático. |
| `POST` | `/api/conciliacion/manual` | Permite el match forzado entre IDs (Requiere motivo). |
| `GET` | `/api/conciliacion/exceptions`| Lista transacciones que no han encontrado par contable. |
| `GET` | `/api/conciliacion/report` | Genera reporte de cierre con balances conciliados. |

## 👥 Roles y Permisos (RBAC)

- **`CFO Holding`:** Acceso total, puede certificar cierres mensuales.
- **`Auditor`:** Solo lectura, acceso a la bitácora SHA-256.
- **`Gerente Filial`:** Solo puede conciliar transacciones de su propio `tenant_id`.

## 🔒 Regla de Integridad
Toda petición a `/api/conciliacion/manual` debe adjuntar el `correlation_id` del ticket de revisión previo, asegurando que ningún ajuste se haga sin rastro administrativo.

---
**Resultado:** Control total de la liquidez bancaria desde una única interfaz unificada.
