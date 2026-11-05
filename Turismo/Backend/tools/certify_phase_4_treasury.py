import os
import django
import uuid
import logging
from decimal import Decimal
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.treasury_automation.bank_account_model import BankAccount
from apps.treasury_automation.bank_transaction_model import BankTransaction
from apps.treasury_automation.bank_connector import BankConnector
from apps.commercial_engine.models import SaaSInvoice, SaaSSubscription
from apps.commercial_engine.plan_model import SaaSPlan
from apps.companies.models import Company

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PHASE4_CERTIFICATION")

def certify_phase_4():
    logger.info("--- INICIANDO CERTIFICACIÓN FASE 4: TESORERÍA AUTOMÁTICA ---")

    # 1. Setup: Cuenta Bancaria y Factura de Prueba
    account = BankAccount.objects.filter(bank_name="Banco de Sarita").first()
    if not account:
        account = BankAccount.objects.create(
            bank_name="Banco de Sarita",
            account_number="****1234",
            company_id=uuid.uuid4()
        )

    # Crear una factura SaaS para conciliar
    company_name = f"Treasury Corp {uuid.uuid4().hex[:4]}"
    company_code = f"TRES{uuid.uuid4().hex[:2]}"
    company = Company.objects.create(name=company_name, code=company_code)

    plan = SaaSPlan.objects.first()
    sub = SaaSSubscription.objects.create(
        company_id=company.id,
        plan=plan,
        renewal_date=date.today(),
        status=SaaSSubscription.Status.ACTIVE
    )

    invoice_number = f"INV-CERT-444-{uuid.uuid4().hex[:4]}"
    invoice = SaaSInvoice.objects.create(
        number=invoice_number,
        subscription=sub,
        company_id=company.id,
        issue_date=date.today(),
        due_date=date.today(),
        total_amount=Decimal('100000.00')
    )
    logger.info(f"Factura generada para conciliación: {invoice.number} por {invoice.total_amount}")

    # 2. Simular Importación de 1000 Transacciones (Stress Test)
    logger.info("Importando 1,000 transacciones...")
    transactions = []

    # Una transacción exacta para la factura anterior
    transactions.append({
        'external_id': f"tx_exact_{uuid.uuid4().hex[:6]}",
        'date': date.today(),
        'description': "Pago Suscripción CERT",
        'amount': Decimal('100000.00'),
        'direction': 'IN',
        'reference': invoice_number
    })

    # Una transacción con comisión (97% del monto)
    transactions.append({
        'external_id': f"tx_fee_{uuid.uuid4().hex[:6]}",
        'date': date.today(),
        'description': "Pago Suscripción con comisión",
        'amount': Decimal('97000.00'),
        'direction': 'IN',
        'reference': "OTHER_REF"
    })

    # Otras 998 transacciones genéricas
    for i in range(998):
        transactions.append({
            'external_id': f"tx_bulk_{i}_{uuid.uuid4().hex[:6]}",
            'date': date.today(),
            'description': f"Movimiento masivo {i}",
            'amount': Decimal('5000.00'),
            'direction': 'IN' if i % 2 == 0 else 'OUT',
            'reference': ''
        })

    imported = BankConnector.import_transactions(account.id, transactions)
    logger.info(f"Transacciones importadas: {imported}")

    # 3. Verificaciones
    # Verificar que la factura se concilió automáticamente
    tx_exact = BankTransaction.objects.filter(reference=invoice_number, reconciliation_status='MATCHED').first()
    if not tx_exact:
        logger.error("❌ No se encontró la transacción conciliada exacta.")
        return False

    logger.info(f"Estado de conciliación exacta: {tx_exact.reconciliation_status}")

    # Verificar Balance General de Cashflow
    from apps.treasury_automation.cashflow_engine import CashflowEngine
    balance = CashflowEngine.get_current_balance()
    logger.info(f"Balance de Tesorería calculado: {balance}")

    # CERTIFICACIÓN
    if imported >= 1000 and tx_exact.matched:
        logger.info("✅ FASE 4 CERTIFICADA EXITOSAMENTE")
        return True

    return False

certify_phase_4()
