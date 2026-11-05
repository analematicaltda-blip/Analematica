# INTEGRACIÓN SEGURA: MONEDERO SOBERANO — SARITA 2026

## 🎯 Objetivo (Bloque 5)
Sincronizar de forma blindada las transacciones externas provenientes del sistema estatal con el núcleo de conciliación de Sarita.

## 🔐 Protocolo de Sincronización

### 1. Autenticación y Firma
- **OAuth2:** El conector utilizará un ClientID/Secret seguro para obtener el token de acceso.
- **Firma Digital:** Cada ráfaga de transacciones recibida debe ser validada contra la **Firma Pública del Monedero**, garantizando el origen legítimo de los datos.

### 2. Flujo de Descarga (Sync Process)
1.  **Request:** Consulta de transacciones por `period_id` o `timestamp`.
2.  **Deduplicación:** El sistema verificará el `external_id`. Si ya existe en la tabla `BancoTransaction`, se ignora para evitar duplicidad de saldos.
3.  **Registro SHA-256:** Se guarda el payload original en el log de auditoría con un hash de integridad, permitiendo auditorías forenses posteriores.

## 🛡️ Control de Errores y Reintentos
- **Retry Policy:** Ante fallos de conexión (HTTP 5xx), el sistema reintentará 3 veces con backoff exponencial.
- **Quarantine:** Transacciones con montos anómalos o firmas inválidas se moverán a un estado de **Cuarentena**, bloqueando su uso en la conciliación hasta intervención manual del Super Admin.

---
**Resultado:** Sincronización 100% auditable y libre de duplicados con la banca externa.
