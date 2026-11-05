# INTEGRACIÓN FRONTEND: TORRE DE CONTROL — SARITA 2026

## 🎨 Bloque 5.2: Activación de la Interfaz Real

Se procede a la desconexión definitiva de los datos estáticos en el Dashboard Ejecutivo (`/dashboard/admin-plataforma/analitica`).

### 1. Indicador de Estado del Cálculo
Cada métrica en la UI debe mostrar su estatus de frescura:
- 🟢 **READY:** Calculado con datos del Ledger cerrados.
- 🟡 **STALE:** Datos en proceso de consolidación.
- 🔴 **ERROR:** Discrepancia matemática detectada.

### 2. Trazabilidad Visual
Al hacer clic en un KPI (ej: ROI 3.4x), el frontend disparará un modal de **"Auditoría de Origen"**:
- Muestra el `snapshot_id` del backend.
- Lista las cuentas del Ledger involucradas.
- Muestra la fecha/hora exacta de la última agregación.

### 3. Error Handling (Fase Final)
Si el endpoint `/api/kpis/control-tower` devuelve un error 500 o inconsistencia, el frontend **no ocultará el fallo**. Mostrará el componente `SovereignWarning`: *"Atención: El motor analítico detectó una discrepancia en el balance; los KPIs estratégicos han sido suspendidos por seguridad institucional"*.

---
**Firmado:** Jules, Software Engineer Audit.
