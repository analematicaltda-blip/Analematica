# PROTOCOLO DE REVERSIÓN Y BLOQUEO FISCAL — SARITA 2026

## ↩️ Bloque 7: Reversión Automática Inmutable

En Sarita, **no se permite borrar ni editar** transacciones contables una vez posteadas. Si una factura se anula comercialmente, se dispara el siguiente flujo:

1.  **Trigger:** EventBus recibe el evento `SALE_REVERSED`.
2.  **Búsqueda:** El sistema localiza el `original_journal_entry_id`.
3.  **Acción:** Se genera un nuevo `JournalEntry` con los montos invertidos (Débito <-> Crédito).
4.  **Vínculo:** El nuevo asiento se marca con `is_reversal = True` y referencia al ID original.
5.  **Notificación:** Emisión de `ACCOUNTING_ENTRY_REVERSED`.

## 🔒 Bloque 8: Bloqueo por Periodo Fiscal

Para garantizar el cierre contable oficial (mensual/anual):

- **Regla Inviolable:** Ningún soldado puede escribir en un periodo marcado como `CLOSED` o `LOCKED`.
- **Excepción de Reversión:** Si la anulación de una venta ocurre sobre un periodo cerrado, el asiento de reversión debe crearse en el **periodo actual abierto**, manteniendo la referencia al documento histórico.

---
**Resultado:** Integridad fiscal garantizada y cumplimiento con estándares internacionales de auditoría contable.
