# RECUPERACIÓN Y SEGURIDAD OPERATIVA — SARITA 2026

## 🏥 Bloque 4: Recuperación Ante Fallas (Self-Healing)

### 4.1 Reconciliador Automático Nocturno
Cada noche, el sistema ejecutará un proceso de integridad total para cada Tenant:

1.  **Validación de Ecuación Contable:** Suma total de `ASSETS` == Suma total de `LIABILITIES` + `EQUITY`.
2.  **Verificación de Libro Mayor:** Comparar el saldo actual de cada `Account` con la suma de todas sus líneas de transacciones en el historial.
3.  **Acción:** Si se detecta una diferencia > 0.001, se bloquea la creación de nuevos asientos para ese Tenant y se dispara una alerta nivel `CRITICAL` al Super Admin.

## 🔐 Bloque 5: Seguridad en Operaciones Críticas

### 5.1 Protocolo de Confirmación Doble (MFA Operativo)
Las siguientes acciones requieren una confirmación secundaria (OTP o Sello de Agente N2):
- Cierre fiscal mensual/anual.
- Eliminación de documentos (Solo permitido en fase Borrador).
- Ajustes contables manuales de alto monto.

### 5.2 Auditoría Forense Extendida
El registro de auditoría (`AuditLog`) para estas operaciones incluirá metadatos de red obligatorios:
- `client_ip`: Dirección IP del origen.
- `user_agent`: Identificador del dispositivo/navegador.
- `geo_location`: Ubicación aproximada (vía IP) para detectar anomalías de acceso geográfico.
- `request_id`: ID de rastreo para correlacionar logs de servidor con logs de aplicación.

---
**Resultado:** Sistema resiliente capaz de detectar corrupciones de datos en menos de 24 horas y blindado contra errores operativos fatales.
