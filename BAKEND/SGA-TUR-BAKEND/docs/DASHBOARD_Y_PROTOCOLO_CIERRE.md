# DASHBOARD EJECUTIVO Y PROTOCOLO DE CIERRE — SARITA 2026

## 📊 Bloque 13: Dashboard en Tiempo Real (Torre de Control)

La Torre de Control del Holding consumirá el `ConsolidationEngine` para proyectar:
- **EBITDA Consolidado:** Margen neto operativo de todo el grupo.
- **Liquidez del Grupo:** Suma de saldos en monederos digitales y cuentas bancarias de todos los tenants.
- **Deuda Intercompany:** Visualización de saldos pendientes de eliminar.
- **Exposure Index:** Riesgo país/región basado en el volumen de transacciones locales.

## 🔒 Bloque 17: Protocolo de Cierre Mensual Consolidado

Aunque la consolidación es "viva", el cierre oficial (auditado) seguirá estos pasos:

1.  **Pre-cierre:** Bloqueo de creación de nuevos asientos en todas las filiales para el mes `M`.
2.  **Validación IC:** El sistema confirma que `Total IC Assets == Total IC Liabilities`.
3.  **Snapshot Inmutable:** Generación de un `ConsolidatedReportSnapshot` en formato JSON.
4.  **Sello Criptográfico:** El snapshot se firma con el **Hash SHA-256** del estado final.
5.  **Certificación:** El CFO Holding marca el registro como `is_certified = True`.

---
**Criterio de Éxito:** Un reporte consolidado certificado debe poder generarse en menos de **2 horas** tras el cierre de la última filial, eliminando las semanas de conciliación manual tradicional.
