# ESCALABILIDAD Y OBSERVABILIDAD SISTÉMICA — SARITA 2026

## 🚀 Bloque 6: Escalabilidad Horizontal (Cloud-Native)

### 6.1 Estrategia de Sharding de Base de Datos
Para soportar el crecimiento de 100 a 100,000 tenants, se aplicará el siguiente modelo:
- **Nivel 1 (Agrupado):** Hasta 1,000 tenants pequeños comparten un cluster de BD optimizado.
- **Nivel 2 (Sharded):** Grupos de tenants por sector geográfico se mueven a bases de datos independientes.
- **Nivel 3 (Dedicado):** Tenants Premium con alto volumen transaccional reciben su propio cluster físico.

### 6.2 Índices Obligatorios para Alto Throughput
Ningún modelo entrará a producción sin estos índices técnicos:
- `btree(tenant_id, created_at)`: Para listados y reportes.
- `hash(correlation_id)`: Para rastreo de eventos.
- `unique(micro_tarea_id)`: Para evitar ejecuciones duplicadas en agentes.

## 👁️ Bloque 8: Observabilidad de Salud Sistémica

### 8.1 Dashboard de SRE (Site Reliability Engineering)
Se implementará una vista centralizada para el Super Admin que reporte:

- **Efectividad de Agentes:** % de `MicroTarea` en estado FAILED.
- **Salud del EventBus:** Latencia entre emisión y procesamiento (Target: < 500ms).
- **Consistencia Ledger:** Conteo de desbalances detectados por el reconciliador nocturno.
- **Throughput:** Transacciones contables por segundo (TPS).

### 8.2 Métricas de Negocio Reales (Torre de Control)
Se eliminan definitivamente los KPIs simulados. Los datos de **ROI, LTV y Churn** se calculan mediante agregaciones directas sobre los modelos de `FacturaVenta` y `JournalEntry`, garantizando la "Verdad Financiera Única".

---
**Resultado:** Infraestructura lista para el crecimiento masivo con visibilidad total sobre el rendimiento y la integridad de los datos.
