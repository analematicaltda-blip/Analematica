# PROTOCOLO DE SEGURIDAD Y GOBERNANZA CONTABLE — SARITA 2026

## 🔐 Bloque 5: Permisos Granulares
Cada acceso a los servicios contables debe validar el permiso específico. El sistema no permite roles genéricos para finanzas.

| Endpoint | Permiso Requerido | Acción |
| :--- | :--- | :--- |
| `GET /asientos` | `contabilidad.ver.asientos` | Lectura de diario. |
| `POST /reverse` | `contabilidad.reversar.asiento` | Sello de anulación. |
| `GET /balance` | `contabilidad.ver.balance` | Acceso a situación financiera. |

## 🛡️ Bloque 6 & 7: Multi-tenant y Protección de Datos
1.  **Aislamiento:** El `tenant_id` se extrae del JWT. Si un usuario intenta inyectar `?tenant_id=XXX` en la URL, el sistema ignora el parámetro y usa el ID del token.
2.  **Sanitización:** Los parámetros de fechas y montos se validan contra el esquema Marshmallow/Pydantic antes de tocar el ORM.
3.  **Logs de Acceso:** Cada llamada a un reporte financiero genera un registro en `AuditLog` con la IP, el usuario y la referencia del documento consultado.

---
**Resultado:** La información contable es inaccesible para cualquier actor que no posea la autoridad delegada por el Tenant.
