from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.core_erp.accounting.models import Account, JournalEntry, FiscalPeriod, ChartOfAccounts, LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.journal_service import JournalService
from decimal import Decimal
from datetime import date
import uuid

class ReservationFlowAccountingTest(TestCase):
    """
    Test Suite para validar el flujo completo de una reserva con impacto contable real.
    """

    def setUp(self):
        self.tenant_id = uuid.uuid4()

        # 1. Setup Chart of Accounts
        self.coa = ChartOfAccounts.objects.create(tenant_id=self.tenant_id, name="Test COA")

        # 2. Setup Accounts (Standard codes)
        self.acc_ar = Account.objects.create(tenant_id=self.tenant_id, chart_of_accounts=self.coa, code="130505", name="Accounts Receivable")
        self.acc_revenue = Account.objects.create(tenant_id=self.tenant_id, chart_of_accounts=self.coa, code="413501", name="Revenue - Commission")
        self.acc_payable = Account.objects.create(tenant_id=self.tenant_id, chart_of_accounts=self.coa, code="233505", name="Payable to Provider")
        self.acc_cash = Account.objects.create(tenant_id=self.tenant_id, chart_of_accounts=self.coa, code="111005", name="Cash / Bank")

        # 3. Setup Fiscal Period
        self.period = FiscalPeriod.objects.create(tenant_id=self.tenant_id, period_start="2026-01-01", period_end="2026-12-31", status="open")

    def test_complete_reservation_flow(self):
        """
        Simula el ciclo de vida contable de una reserva: Confirmación -> Pago Cliente -> Pago Proveedor.
        """

        # --- PASO 1: Reserva Confirmada ($1,000) ---
        payload_confirm = {
            "tenant_id": str(self.tenant_id),
            "total_amount": 1000.0,
            "commission_rate": 0.10,
            "reference": "RES-001"
        }

        entry_confirm = LedgerEngine.post_event("ReservationConfirmed", payload_confirm)
        self.assertIsNotNone(entry_confirm)
        self.assertTrue(entry_confirm.is_posted)

        # Verificar líneas
        lines = entry_confirm.lines.all()
        self.assertEqual(lines.filter(account=self.acc_ar).first().debit_amount, Decimal('1000.00'))
        self.assertEqual(lines.filter(account=self.acc_revenue).first().credit_amount, Decimal('100.00'))
        self.assertEqual(lines.filter(account=self.acc_payable).first().credit_amount, Decimal('900.00'))

        # --- PASO 2: Pago Recibido ($1,000) ---
        payload_payment = {
            "tenant_id": str(self.tenant_id),
            "amount": 1000.0,
            "reference": "RES-001"
        }
        entry_payment = LedgerEngine.post_event("PaymentReceived", payload_payment)
        self.assertTrue(entry_payment.is_posted)

        lines_p = entry_payment.lines.all()
        self.assertEqual(lines_p.filter(account=self.acc_cash).first().debit_amount, Decimal('1000.00'))
        self.assertEqual(lines_p.filter(account=self.acc_ar).first().credit_amount, Decimal('1000.00'))

        # --- PASO 3: Pago al Proveedor ($900) ---
        payload_provider = {
            "tenant_id": str(self.tenant_id),
            "amount": 900.0,
            "reference": "RES-001"
        }
        entry_prov = LedgerEngine.post_event("ProviderPaid", payload_provider)
        self.assertTrue(entry_prov.is_posted)

        lines_v = entry_prov.lines.all()
        self.assertEqual(lines_v.filter(account=self.acc_payable).first().debit_amount, Decimal('900.00'))
        self.assertEqual(lines_v.filter(account=self.acc_cash).first().credit_amount, Decimal('900.00'))

    def test_reservation_reversal_on_cancellation(self):
        """
        Valida que la cancelación genere una reversión exacta del asiento original.
        """
        payload_confirm = {
            "tenant_id": str(self.tenant_id),
            "total_amount": 1000.0,
            "commission_rate": 0.10,
            "reference": "RES-CANCEL-001"
        }
        entry_confirm = LedgerEngine.post_event("ReservationConfirmed", payload_confirm)

        # Ejecutar reversión
        reversal_entry = LedgerEngine.reverse_entry(entry_confirm.id, reason="Cliente canceló")

        self.assertTrue(reversal_entry.is_reversal)
        self.assertEqual(reversal_entry.reversed_entry_id, entry_confirm.id)

        # Verificar que los montos se invirtieron
        lines_r = reversal_entry.lines.all()
        self.assertEqual(lines_r.filter(account=self.acc_ar).first().credit_amount, Decimal('1000.00'))
        self.assertEqual(lines_r.filter(account=self.acc_revenue).first().debit_amount, Decimal('100.00'))
        self.assertEqual(lines_r.filter(account=self.acc_payable).first().debit_amount, Decimal('900.00'))
