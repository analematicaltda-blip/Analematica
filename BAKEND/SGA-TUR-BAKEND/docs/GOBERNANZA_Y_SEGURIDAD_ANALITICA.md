# GOBERNANZA Y SEGURIDAD ANALÍTICA — SARITA 2026

## 🏛️ Bloque 10: Gobernanza de Métricas

Se establece el **Comité de Soberanía de Datos** como el único ente capaz de autorizar cambios estructurales en la Torre de Control.

1.  **Cambio de Fórmulas:** Cualquier ajuste en un KPI (ej: cambiar 45 por 60 días de inactividad para Churn) debe registrarse como una `StrategicPolicy` en el `GovernanceKernel`.
2.  **Versionamiento:** Cada cambio incrementa la `methodology_version`. Se prohíbe re-calcular el pasado con reglas nuevas (Inmutabilidad Histórica).

## 🔐 Bloque 11: Blindaje Técnico

1.  **Hash de Snapshot:** Al generarse el set de KPIs diario, el `TaxAuditLogger` (o equivalente analítico) creará un hash SHA-256 de los resultados.
2.  **Validación de Dataset:** El sistema verifica que la suma de ingresos de los KPIs coincida con el total acreditado en la cuenta 41xx del Ledger. Si existe discrepancia > 1%, el KPI se marca como `ERROR_CONSISTENCIA`.
3.  **Logs de Consulta:** Se registra qué usuario ejecutivo visualizó qué métrica, incluyendo IP y UserAgent para trazabilidad de filtración de datos.

---
**Resultado:** La Torre de Control deja de ser un "Dashboard de visualización" para ser una **"Prueba de Verdad Institucional"**.
