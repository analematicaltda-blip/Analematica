import os
import django
import sys
from decimal import Decimal

# Añadir el directorio actual al path para importar apps
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def run_certification():
    print("\n" + "="*50)
    print("🚀 CERTIFICACIÓN FASE 1: NÚCLEO ERP REAL (SARITA)")
    print("="*50)

    try:
        from apps.core_erp.accounting_engine import AccountingEngine
        from apps.core_erp.billing_engine import BillingEngine
        from apps.core_erp.treasury_engine import TreasuryEngine
        from apps.core_erp.chart_of_accounts import ChartOfAccountsManager
        from apps.core_erp.event_bus import EventBus
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return

    # 1. Validación de Estructura Lógica
    print("\n1. ESTRUCTURA BASE:")
    mandatory = ChartOfAccountsManager.get_mandatory_accounts()
    if 'INCOME_SAAS' in mandatory and 'DEFERRED_INCOME' in mandatory:
        print("   [OK] Cuentas SaaS e Ingresos Diferidos presentes en COA.")
    else:
        print("   [FAIL] Faltan cuentas críticas en el Plan de Cuentas.")
        return

    # 2. Prueba del Motor Contable (Balance)
    print("\n2. MOTOR CONTABLE (Balance):")
    class MockEntry:
        def __init__(self, debit, credit):
            self.id = "TEST-ENTRY"
            self.is_posted = False
            self.lines = type('Lines', (), {'all': lambda: [
                type('L', (), {'debit': Decimal(debit), 'credit': Decimal('0.00')}),
                type('L', (), {'debit': Decimal('0.00'), 'credit': Decimal(credit)})
            ]})
        def save(self): pass

    valid_entry = MockEntry('100.00', '100.00')
    invalid_entry = MockEntry('100.00', '90.00')

    try:
        AccountingEngine.validate_balance(valid_entry)
        print("   [OK] Validación de balance correcto exitosa.")
    except Exception as e:
        print(f"   [FAIL] Falló validación de balance correcto: {e}")
        return

    try:
        AccountingEngine.validate_balance(invalid_entry)
        print("   [FAIL] No detectó asiento descuadrado.")
        return
    except Exception:
        print("   [OK] Detección de asiento descuadrado exitosa.")

    # 3. Prueba del Motor de Facturación
    print("\n3. MOTOR DE FACTURACIÓN (BillingEngine):")
    class MockInvoice:
        def __init__(self):
            self.number = "FAC-CERT-001"
            self.status = "DRAFT"
            self.total_amount = Decimal('0.00')
            self.tax_amount = Decimal('0.00')
            self.lines = type('Lines', (), {'all': lambda: [
                type('L', (), {'subtotal': Decimal('100.00'), 'tax_amount': Decimal('19.00')})
            ]})
        def save(self): pass

    invoice = MockInvoice()
    BillingEngine.calculate_totals(invoice)
    if invoice.total_amount == Decimal('119.00'):
        print(f"   [OK] Cálculo de totales BillingEngine correcto: {invoice.total_amount}")
    else:
        print(f"   [FAIL] Error en cálculo de totales: {invoice.total_amount}")
        return

    # 4. Prueba del Motor de Tesorería
    print("\n4. MOTOR DE TESORERÍA (TreasuryEngine):")
    try:
        TreasuryEngine.apply_payment(invoice, Decimal('119.00'), 'CASH', 'REF-001')
        print("   [OK] Flujo de aplicación de pago completado.")
    except Exception as e:
        print(f"   [FAIL] Error en TreasuryEngine: {e}")
        return

    # 5. Prueba del Bus de Eventos
    print("\n5. ARQUITECTURA DIRIGIDA POR EVENTOS (EventBus):")
    event_received = False
    def test_callback(payload):
        nonlocal event_received
        event_received = True
        print(f"   [OK] Suscriptor recibió evento con payload: {payload}")

    EventBus.subscribe(EventBus.INVOICE_CREATED, test_callback)
    EventBus.emit(EventBus.INVOICE_CREATED, {'invoice_id': 'CERT-001'})

    if event_received:
        print("   [OK] Bus de eventos operativo.")
    else:
        print("   [FAIL] Bus de eventos no disparó el callback.")
        return

    print("\n" + "="*50)
    print("✅ FASE 1 CERTIFICADA: EL NÚCLEO ERP ES SÓLIDO")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_certification()
