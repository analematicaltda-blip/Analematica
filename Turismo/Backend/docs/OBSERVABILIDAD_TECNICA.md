# OBSERVABILIDAD TÉCNICA — SARITA 2026

## 🎯 Objetivo (Bloque 23)
Garantizar la visibilidad total de la infraestructura y el rendimiento del sistema mediante una capa de observabilidad integrada en la Torre de Control.

## 📊 23.1 Métricas Técnicas Críticas
Se incorporan al `MetricRegistry` para monitoreo en tiempo real:

| Métrica | Dominio | Unidad | Descripción |
| :--- | :--- | :--- | :--- |
| `API_LATENCY_P99` | INFRA | ms | Latencia del 99% de las peticiones API. |
| `EVENT_BUS_THROUGHPUT` | INFRA | msg/sec | Mensajes procesados por el EventBus por segundo. |
| `DB_CONNECTION_POOL` | INFRA | count | Conexiones activas a la base de datos. |
| `AGENT_REASONING_TIME` | AI | sec | Tiempo promedio de "pensamiento" de un agente. |
| `ERROR_RATE_5XX` | INFRA | % | Tasa de errores de servidor (objetivo < 0.1%). |

## 🛠️ 23.2 Dashboard de Infraestructura (Torre de Control)
El Super Admin podrá visualizar un "System Health Score" (0-100) calculado como:
`Score = (Uptime * 0.4) + (1 - LatencyScore * 0.3) + (1 - ErrorRate * 0.3)`

## 🚀 23.3 Trazabilidad (OpenTelemetry)
- **Trace ID Unificado:** Cada `GovernanceIntention` generará un Trace ID que viajará desde el Frontend, pasando por el Backend, hasta el Soldado N6.
- **Auditoría de Eventos:** Cada mensaje en el `EventBus` queda registrado en la tabla `SystemicObserver` para replay y auditoría.

---
**Resultado:** Capacidad de detección proactiva de fallos antes de que afecten la experiencia del usuario final.
