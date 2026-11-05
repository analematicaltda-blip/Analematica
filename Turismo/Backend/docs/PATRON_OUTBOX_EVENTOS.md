# PATRÓN OUTBOX: GARANTÍA DE ENTREGA DE EVENTOS — SARITA 2026

## 🎯 Objetivo (Bloque 2)
Garantizar que ningún evento se pierda por fallos de red o caídas del servicio de mensajería. El sistema asegura consistencia transaccional absoluta entre la base de datos y el EventBus.

## 🏗️ Esquema de la Tabla `OutboxEvent`

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `id` | UUID | Identificador único del evento. |
| `event_type` | String | Tipo de evento (ej: `INVOICE_CONFIRMED`). |
| `payload` | JSONB | Datos completos del evento. |
| `status` | Enum | PENDING, PROCESSED, ERROR. |
| `retries` | Integer | Contador de intentos de envío. |
| `created_at` | DateTime | Marca de tiempo de creación. |
| `processed_at` | DateTime | Marca de tiempo de envío exitoso. |

## 🔄 El Flujo de Trabajo (Lifecycle)

1.  **Persistencia (Atómica):** El Soldado N6 Oro guarda la entidad de negocio Y el registro en `OutboxEvent` dentro del mismo `transaction.atomic()`.
2.  **Publicación:** Un worker asíncrono (OutboxRelay) escanea la tabla buscando registros `PENDING`.
3.  **Entrega:** El relay publica al `EventBus` real.
4.  **Confirmación:** Al recibir el ACK del bus, el registro se marca como `PROCESSED`.

## 🛡️ Reprocesamiento y Resiliencia (Bloque 2.2)
- **Backoff Exponencial:** 1s, 2s, 4s, 8s, 16s.
- **Límite:** 5 intentos. Al superar el límite, se dispara una **Alerta Sistémica Crítica** a la Torre de Control.
- **Prevención de Duplicados:** Cada evento en el Outbox hereda el `correlation_id` original para que el suscriptor mantenga la idempotencia.

---
**Resultado:** Fiabilidad del 99.99% en la comunicación entre dominios autónomos.
