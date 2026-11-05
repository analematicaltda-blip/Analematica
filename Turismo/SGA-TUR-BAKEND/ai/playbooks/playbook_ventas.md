# Playbook: Gestión de Facturación y Ventas
**Misión:** Garantizar la integridad financiera de cada venta.

## Reglas Operativas
1. **Calcular Impuestos:** Aplicar reglas fiscales según jurisdicción.
2. **Generar Factura:** Ejecutar `BillingService.create_invoice`.
3. **Registrar en Ledger:** Asegurar asiento contable vía `AccountingEngine`.
4. **Validar Pago:** Confirmar recepción de fondos en `WalletService`.
