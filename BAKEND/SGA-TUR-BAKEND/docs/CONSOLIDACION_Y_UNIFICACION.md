# CONSOLIDACIÓN Y UNIFICACIÓN DE IDENTIDAD — SARITA 2026

## 🏛️ Bloque C: Consolidación Holding Real

### 1. Eliminación Intercompany
Se implementará el campo `consolidation_code` en el modelo `Account`.
- **Lógica:** Al consolidar, si el sistema detecta un Débito en el Tenant A y un Crédito en el Tenant B bajo el mismo `consolidation_code`, genera automáticamente un asiento de eliminación en el snapshot del Holding.

### 2. Snapshots Firmados
Cada cierre mensual consolidado producirá un archivo JSON que contiene:
- Balances unificados.
- Detalle de eliminaciones.
- Hash SHA-256 de integridad.
- Firma digital del Super Admin.

## 🆔 Bloque D: Unificación de Identidad (Tenant Raíz)

### Estrategia de Migración
Para eliminar la duplicidad entre `Tenant` y `ProviderProfile`, se seguirá este plan:

1.  **Enlace Fuerte:** Crear un campo `tenant = OneToOneField('core_erp.Tenant')` en `ProviderProfile`.
2.  **Eliminación de Redundancia:** Desactivar los campos `NIT`, `RazonSocial` y `RegimenFiscal` del perfil. Estos datos se consultarán exclusivamente del `Tenant`.
3.  **Integridad Histórica:** Script de migración que asocie los `JournalEntry` antiguos con el nuevo `tenant_id` unificado.

## 📊 Matriz de Estado Final Esperado

| Área | Estado Actual | Estado Post-Plan |
| :--- | :--- | :--- |
| **Identidad** | Fragmentada (Tenant/Profile) | **Unificada (Tenant Raíz)** |
| **Consolidación** | Manual / Simulación | **Automática / Firmada** |
| **Moneda** | Transaccional simple | **Multimoneda con FX Histórico** |

---
**Firmado:** Jules, Software Engineer Audit.
