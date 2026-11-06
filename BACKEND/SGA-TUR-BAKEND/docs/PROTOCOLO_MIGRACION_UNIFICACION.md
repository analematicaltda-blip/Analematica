# PROTOCOLO DE MIGRACIÓN TRANSACCIONAL: UNIFICACIÓN IDENTITARIA — SARITA 2026

## 🎯 Objetivo (Bloque 5.2)
Migrar la base instalada de `ProviderProfiles` hacia la nueva arquitectura de `Tenant` raíz sin pérdida de integridad referencial ni duplicidad de datos.

## 🔄 El Script de Migración (Fases)

### Fase 1: Creación de Huérfanos
1.  Escanear todos los `ProviderProfile` actuales.
2.  Por cada perfil, verificar si tiene un `Tenant` con el mismo `tax_id`.
3.  Si no existe, crear el `Tenant` correspondiente en `core_erp` usando los datos legales del perfil.

### Fase 2: Reasignación de Enlaces (Relinking)
1.  Vincular el `ProviderProfile.tenant_id` con el `Tenant.id` recién creado o encontrado.
2.  Actualizar todas las tablas operativas (Reservas, Facturas, Inventario) para que su `tenant_id` apunte al nuevo `Tenant` central en lugar del perfil local.

### Fase 3: Purga de Redundancia
1.  Eliminar las columnas `legal_name`, `tax_id` y `currency` de la tabla `ProviderProfile`.
2.  Eliminar la tabla `Tenant` obsoleta del dominio comercial (si existe).

## 🛡️ Garantías de Seguridad
- **Atomaticidad:** El script se ejecuta dentro de un bloque `transaction.atomic()`. Si un solo registro falla, se revierte todo.
- **Validación Post-Script:** Comparar el conteo de `ProviderProfile` inicial vs `Tenant` final. Deben ser iguales.

---
**Resultado:** Sistema limpio, normalizado y listo para producción masiva con jerarquía holding.
