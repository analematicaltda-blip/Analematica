# PIPELINE EVENT-DRIVEN DE INVENTARIO — SARITA 2026

## 🛰️ Bloque VII: Sincronización Real mediante Eventos

El sistema abandona el procesamiento batch para pasar a una integración inmediata basada en el EventBus:

1.  **Registro:** El Soldado N6 de Inventario guarda el movimiento y emite el evento `INVENTORY_MOVEMENT_CONFIRMED`.
2.  **AccountingSubscriber:** Intercepta la señal y dispara el motor de reglas de inventario.
3.  **Persistencia:** El `LedgerWriter` crea el asiento con firma SHA-256.
4.  **Confirmación:** Se devuelve el `journal_entry_id` al módulo de inventario para marcar el registro como `SYNCED`.

## 🌃 Bloque IX: Conciliación Automática Nocturna

Cada noche (00:00 UTC), un Capitán de Auditoría ejecutará:

1.  **Recálculo de Kardex:** Reconstruir el saldo físico esperado sumando todos los movimientos desde el génesis.
2.  **Cruce vs Ledger:** Comparar el saldo monetario de la cuenta 14xx contra la valorización del Kardex (Cantidad * Costo Promedio).
3.  **Acción:**
    - Si la diferencia es < 0.1%, se emite reporte de conformidad.
    - Si la diferencia es > 0.1%, se dispara una **Alerta de Bloqueo de Almacén** a la Torre de Control.

---
**Garantía:** No puede existir un cierre de periodo fiscal si existen movimientos con estado `PENDING_SYNC`.
