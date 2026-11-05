# AISLAMIENTO MULTI-TENANT TOTAL — SARITA 2026

## 📜 Propósito (Bloque 3)
Eliminar el riesgo de contaminación cruzada de datos entre empresas (Tenants). El blindaje es tanto a nivel de consulta (Lógico) como a nivel de integridad (Criptográfico).

## 🛡️ 3.1 Filtro Global Obligatorio
El sistema implementará un `GlobalTenantManager` que inyectará automáticamente la cláusula `WHERE tenant_id = 'current_tenant'` en todas las consultas ORM.

**Reglas de Prohibición:**
- ❌ Prohibido el uso de `.objects.all()` en modelos que hereden de `TenantAwareModel`.
- ❌ Prohibido saltar el filtro sin autorización explícita del `GovernanceKernel` (Sello Administrativo).

## 🔐 3.2 Seguridad Criptográfica por Tenant
Cada Tenant poseerá su propia identidad criptográfica independiente para asegurar sus firmas digitales:

1.  **Secret Key Individual:** Clave de 256 bits única por empresa, almacenada en un Vault seguro.
2.  **Salt Independiente:** Todas las firmas SHA-256 de los asientos contables incluirán el salt específico del tenant.
3.  **Resultado:** Si el sistema central es comprometido, los hashes de integridad de un Tenant no pueden ser usados para falsificar registros de otro.

## 🧪 3.3 Protocolo de Test de Aislamiento (Breach Test)

Cada despliegue deberá pasar esta batería de pruebas automatizadas:

- **Cross-Read Block:** El Tenant A intenta consultar un `JournalEntry` por ID perteneciente al Tenant B -> El sistema debe retornar `Http404` o `PermissionError`.
- **Token Swap Test:** Utilizar un JWT del Tenant A para intentar emitir una factura bajo el perfil del Tenant B -> El `AuthGuard` debe invalidar la sesión inmediatamente.

---
**Resultado:** Estanqueidad absoluta de la información financiera y privada de cada cliente.
