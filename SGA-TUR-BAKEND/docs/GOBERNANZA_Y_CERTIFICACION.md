# GOBERNANZA Y PROTOCOLO DE CERTIFICACIÓN — SARITA 2026

## 🛰️ Bloque E: El EventBus como Columna Vertebral

### Reglas de Soberanía Event-Driven
1.  **Aislamiento Total:** Ningún dominio (Comercial, Contable, SST) puede importar modelos de otro. La comunicación es 100% asíncrona vía `EventBus`.
2.  **Observabilidad (`EventLog`):** Se implementará la tabla de seguimiento para cada evento emitido:
    - `EMITTED` -> `ACKNOWLEDGED` -> `PROCESSED` | `FAILED`.

## 🧪 Bloque F: Certificación para Producción Masiva

Antes de habilitar el onboarding para el primer grupo de 100 prestadores, el sistema debe superar esta certificación:

### 1. Stress Test (Autonomía)
- **Carga:** 10,000 ventas en 1 hora.
- **Validación:** 0 desbalances en el Libro Mayor. Todas las facturas deben tener un asiento asociado.

### 2. Test Multi-Tenant (Seguridad)
- **Escenario:** Inyectar una transacción del Tenant A con el `tenant_id` del Tenant B.
- **Resultado:** El `GovernanceKernel` debe bloquear la operación y generar un `ForensicSecurityLog`.

### 3. Auditoría de Integridad SHA-256
- **Procedimiento:** Tomar una muestra aleatoria de 20 `JournalEntry`. Recalcular el hash manualmente y compararlo con el `system_hash` en BD.
- **Meta:** 100% de coincidencia.

---
**Aval Final:** Tras superar estos tests, SARITA recibirá el sello **"Production Ready: Sovereign Standard v1.0"**.
