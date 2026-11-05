# MECANISMOS DE INTEGRIDAD Y CONSISTENCIA — SARITA 2026

## 🆔 Bloque 4: Control de Idempotencia (`ProcessedEvents`)

Para evitar la duplicidad de asientos contables ante reintentos de red, se implementará la tabla de control:

| Campo | Regla |
| :--- | :--- |
| `event_id` | PK - UUID (Heredado del evento raíz). |
| `status` | `SUCCESS` | `FAILED`. |
| `target_entity_id` | UUID del `JournalEntry` creado. |
| `correlation_id` | Para rastreo de cadena. |

**Lógica:** Si `status == SUCCESS`, el sistema ignora cualquier petición duplicada con el mismo `event_id`.

## 🔒 Bloque 10: Auditoría Forense con Hashes Encadenados

Cada asiento generado por el pipeline será sellado mediante:
`integrity_hash = SHA256(prev_hash + current_payload + timestamp)`

- **Garantía:** Si un atacante modifica un monto en la DB, la cadena de hashes se rompe, alertando inmediatamente a la Torre de Control.

## 📦 Bloque 11: Outbox Pattern (Consistencia DB + Evento)

El evento `ACCOUNTING_ENTRY_CREATED` no se emite "al aire". Se guarda en la tabla `OutboxEvent` dentro de la transacción del asiento.
- **Worker:** Un proceso en segundo plano lee el Outbox y garantiza que el mensaje llegue al `EventBus`.
- **Beneficio:** Si el servidor se apaga justo después de guardar el asiento pero antes de emitir el evento, el worker lo enviará al reiniciar.

---
**Resultado:** Integridad absoluta y 0% de pérdida de sincronización entre el Ledger y el resto del sistema.
