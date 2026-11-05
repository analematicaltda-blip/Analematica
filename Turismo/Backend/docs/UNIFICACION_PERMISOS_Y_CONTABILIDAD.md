# UNIFICACIÓN DE PERMISOS Y CONTABILIDAD — SARITA 2026

## 🔐 Bloque 5.3: Autorización Centralizada en Tenant

Se prohíbe asociar permisos directamente a perfiles de negocio. El nuevo flujo de autorización será:

1.  **Contexto:** El usuario inicia sesión y selecciona su `Tenant` de trabajo.
2.  **Validación:** El `PermissionManager` consulta: `UserRole.objects.filter(user=request.user, tenant=current_tenant)`.
3.  **Aislamiento:** Un usuario puede ser 'Admin' en el Tenant A pero solo 'Observador' en el Tenant B. La autoridad nace y muere en los límites del `Tenant`.

## 🧾 Bloque 5.4: Sincronización Contable Determinística

El `LedgerEngine` dejará de reconocer al `ProviderProfile` como sujeto contable.

- **Single Point of Entry:** Todo asiento (`JournalEntry`) DEBE tener un `tenant_id` válido apuntando a `core_erp.Tenant`.
- **Integridad:** Si un evento de nómina o inventario llega al dominio contable referenciando un perfil, el sistema resolverá automáticamente el `tenant_id` a través del enlace OneToOne antes de la persistencia.
- **Reporting:** Los reportes de Balance General y P&L se agruparán exclusivamente por `Tenant`.

---
**Firmado:** Jules, Software Engineer Audit.
