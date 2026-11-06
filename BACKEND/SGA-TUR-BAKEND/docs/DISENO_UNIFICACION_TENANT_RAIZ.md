# UNIFICACIÓN ESTRUCTURAL: TENANT COMO RAÍZ UNIVERSAL — SARITA 2026

## 🏛️ El Nuevo Modelo de Identidad (Bloque 4)

Se establece al `Tenant` como la única entidad de identidad organizacional en el sistema. El `ProviderProfile` deja de ser una entidad paralela para convertirse en una extensión funcional.

### 1. Entidad Raíz: `Tenant` (Core ERP)
```python
class Tenant(BaseErpModel):
    # Identidad Legal
    legal_name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=100, default='Colombia')
    currency = models.CharField(max_length=3, default='COP')

    # Jerarquía y Tipo (Bloque 4)
    class TenantType(models.TextChoices):
        HOLDING = 'HOLDING', 'Holding'
        SUBSIDIARY = 'SUBSIDIARY', 'Subsidiaria'
        PROVIDER = 'PROVIDER', 'Prestador de Servicio'
        CLIENT = 'CLIENT', 'Cliente Corporativo'
    tenant_type = models.CharField(max_length=20, choices=TenantType.choices)
    parent_tenant = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='subsidiaries')

    status = models.CharField(max_length=20, default='ACTIVE')
```

### 2. Extensión Funcional: `ProviderProfile` (Domain Business)
```python
class ProviderProfile(BaseErpModel):
    # Enlace Inviolable (Bloque 5.1)
    tenant = models.OneToOneField('core_erp.Tenant', on_delete=models.CASCADE, related_name='profile')

    # Metadatos Operativos (Especialización)
    service_categories = models.JSONField(default=list)
    banking_information = models.JSONField(default=dict)
    compliance_flags = models.JSONField(default=dict)
```

## 🔐 Reglas de Aislamiento
- Todo modelo `TenantAwareModel` debe apuntar a `core_erp.Tenant`.
- El filtro de consultas (`GlobalTenantManager`) se aplicará exclusivamente sobre el `tenant_id`.

---
**Resultado:** Una sola fuente de verdad. El sistema sabe que la "Empresa X" tiene una identidad legal (`Tenant`) y una configuración operativa (`ProviderProfile`).
