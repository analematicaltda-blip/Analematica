# ESTRATEGIA DE UNIFICACIÓN DE IDENTIDAD Y CONSOLIDACIÓN HOLDING — SARITA 2026

## 🆔 Unificación Tenant / ProviderProfile (Bloque 4)

### Diagnóstico del Conflicto
Actualmente, el sistema posee una fragmentación de identidad:
- `Tenant` (Capa de Infraestructura SaaS)
- `ProviderProfile` (Capa de Negocio "Mi Negocio")

### Resolución: "Un Solo Origen de Verdad"
1.  **Redefinición de Jerarquía:** El `Tenant` se convierte en la entidad raíz obligatoria.
2.  **Referenciación Unificada:** El `ProviderProfile` dejará de duplicar campos fiscales. Heredará toda la autoridad del `Tenant`.
3.  **Vínculo Técnico:** Se establecerá una FK (Foreign Key) 1:1 estricta entre `Tenant` y `ProviderProfile`. Todas las consultas contables se filtrarán exclusivamente por el `tenant_id`.

## 🏛️ Consolidación Automática Holding (Bloque 3)

### Snapshots Consolidados
Para garantizar el reporte en tiempo real sin procesos batch lentos, se implementará el **Snapshot de Consolidación**:

1.  **Eliminación Intercompany:** El sistema detectará transacciones entre Tenants del mismo Holding (ej: Agencia A compra a Hotel B) y generará el asiento de eliminación automático basado en el código de consolidación.
2.  **Conversión de Moneda:** Se utilizará la `FXRateTable` histórica para convertir los balances de cada subsidiaria a la moneda base del Holding al momento del reporte.
3.  **Snapshot Inmutable:** Cada cierre consolidado generará un JSON firmado con SHA-256, permitiendo auditorías retroactivas sin posibilidad de alteración.

### Reportes del Holding (Torre de Control)
- **EBITDA Consolidado:** Suma de Net Profits de todos los Tenants.
- **Exposure Index:** Riesgo sistémico consolidado del ecosistema.
- **Liquidity Buffer:** Caja total disponible en el monedero digital del Holding.

---
**Impacto:** Sarita deja de ser una "Federación de Empresas" para convertirse en un **Corporativo Digital Unificado**.
