# ESPECIFICACIÓN: PIPELINE DE SINCRONIZACIÓN DETERMINÍSTICA VENTAS → CONTABILIDAD

## 🎯 Objetivo (Bloque 2.1)
Garantizar que ninguna factura comercial confirmada quede en el limbo contable. El flujo pasa de ser una decisión de la IA a ser una consecuencia determinística de las reglas de negocio.

## 🔄 El Flujo de Sincronización

1.  **Trigger:** El dominio de Ventas emite el evento `SALE_CONFIRMED` al `EventBus`.
2.  **Subscriber:** El `AccountingSubscriber` intercepta el evento.
3.  **Engine:** Se consulta el `PostingRulesEngine` para obtener las cuentas de Débito, Crédito e Impuestos según el país y tipo de servicio.
4.  **Action:** El `SoldadoLedgerWriter` (N6 Oro) ejecuta la escritura en el `LedgerEngine` central.
5.  **Output:** Se emite el evento `ACCOUNTING_ENTRY_CREATED` para actualizar el Holding.

## 📝 Reglas Contables Determinísticas (Bloque 2.2)

| Escenario | Cuenta Débito (1) | Cuenta Crédito (4) | Cuenta Impuesto (2) |
| :--- | :--- | :--- | :--- |
| **Venta Servicio Hotelero** | 1305 (CxC Clientes) | 4135 (Ingresos Hoteleros) | 2408 (IVA 19%) |
| **Venta Gastronómica** | 1105 (Caja General) | 4135 (Ingresos Alimentos) | 2805 (Impuesto Consumo) |
| **Comisión Agencia** | 1305 (CxC Clientes) | 4135 (Servicios Turismo) | 2408 (IVA 19%) |

## 🛡️ Validación de Balance (Bloque 2.3)

Antes de persistir cualquier asiento, el `LedgerEngine` aplicará la siguiente validación lógica:

```python
def validate_balance(debits: List, credits: List):
    total_debit = sum(d.amount for d in debits)
    total_credit = sum(c.amount for c in credits)

    if abs(total_debit - total_credit) > 0.001:
        raise UnbalancedAccountingEntryError(
            f"Desbalance detectado: Débito ${total_debit} != Crédito ${total_credit}"
        )
```

## 🧪 Matriz de Pruebas de Integridad
- **Test Venta Simple:** Confirmar venta -> Verificar asiento automático.
- **Test Reversión:** Anular factura -> Verificar asiento inverso automático.
- **Test Idempotencia:** Recibir el mismo evento `SALE_CONFIRMED` dos veces -> Verificar que solo exista un asiento.

---
**Resultado:** La contabilidad deja de ser un "módulo" para convertirse en un "reflejo" atómico de la operación comercial.
