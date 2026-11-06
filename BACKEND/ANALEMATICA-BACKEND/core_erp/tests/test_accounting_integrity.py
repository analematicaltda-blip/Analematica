from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.core_erp.accounting.models import Account, JournalEntry, FiscalPeriod, ChartOfAccounts, LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.journal_service import JournalService
from decimal import Decimal
from datetime import date
import uuid

class AccountingIntegrityTest(TestCase):
    """
    Test Suite para validar la integridad del núcleo contable centralizado.
    """

    def setUp(self):
        self.org_1 = uuid.uuid4()
        self.org_2 = uuid.uuid4()

        # Org 1 Setup
        self.coa_1 = ChartOfAccounts.objects.create(tenant_id=self.org_1, name="COA Org 1")
        self.acc_1_asset = Account.objects.create(tenant_id=self.org_1, chart_of_accounts=self.coa_1, code="110505", name="Caja")
        self.acc_1_rev = Account.objects.create(tenant_id=self.org_1, chart_of_accounts=self.coa_1, code="413501", name="Ingresos")
        self.period_1 = FiscalPeriod.objects.create(tenant_id=self.org_1, period_start="2026-01-01", period_end="2026-12-31", status="open")

        # Org 2 Setup
        self.coa_2 = ChartOfAccounts.objects.create(tenant_id=self.org_2, name="COA Org 2")
        self.acc_2_asset = Account.objects.create(tenant_id=self.org_2, chart_of_accounts=self.coa_2, code="110505", name="Caja")
        self.period_2 = FiscalPeriod.objects.create(tenant_id=self.org_2, period_start="2026-01-01", period_end="2026-12-31", status="open")

    def test_balanced_entry_success(self):
        """Valida que un asiento balanceado se postea correctamente."""
        lines = [
            {'account': self.acc_1_asset, 'debit': 1000.0, 'credit': 0},
            {'account': self.acc_1_rev, 'debit': 0, 'credit': 1000.0}
        ]
        entry = JournalService.create_entry(
            tenant_id=str(self.org_1),
            entry_date=date(2026, 5, 20),
            description="Venta balanceada",
            lines_data=lines
        )

        posted_entry = LedgerEngine.post_entry(entry.id)
        self.assertTrue(posted_entry.is_posted)

    def test_unbalanced_entry_fails(self):
        """Valida que un asiento descuadrado sea rechazado."""
        from apps.core_erp.accounting.exceptions import UnbalancedEntryError
        lines = [
            {'account': self.acc_1_asset, 'debit_amount': 1000.0, 'credit_amount': 0},
            {'account': self.acc_1_rev, 'debit_amount': 0, 'credit_amount': 900.0} # Descuadre de 100
        ]
        entry = JournalService.create_entry(
            tenant_id=str(self.org_1),
            entry_date=date(2026, 5, 20),
            description="Venta descuadrada",
            lines_data=lines
        )

        with self.assertRaises(UnbalancedEntryError):
            LedgerEngine.post_entry(entry.id)

    def test_multi_tenant_isolation(self):
        """Valida que los asientos de un tenant no sean visibles/modificables por otro."""
        lines = [
            {'account': self.acc_1_asset, 'debit': 500.0, 'credit': 0},
            {'account': self.acc_1_rev, 'debit': 0, 'credit': 500.0}
        ]
        entry_org_1 = JournalService.create_entry(
            tenant_id=str(self.org_1),
            entry_date=date(2026, 5, 20),
            description="Asiento Org 1",
            lines_data=lines
        )

        # Verificar que Org 2 no tiene acceso a este asiento (a nivel lógico/query)
        self.assertEqual(JournalEntry.objects.filter(tenant_id=self.org_2).count(), 0)
        self.assertEqual(JournalEntry.objects.filter(tenant_id=self.org_1).count(), 1)

    def test_closed_period_prevention(self):
        """Valida que no se pueda postear en un periodo cerrado."""
        self.period_1.status = 'closed'
        self.period_1.save()

        lines = [
            {'account': self.acc_1_asset, 'debit_amount': 100.0, 'credit_amount': 0},
            {'account': self.acc_1_rev, 'debit_amount': 0, 'credit_amount': 100.0}
        ]
        # JournalService fails early if no open period is found
        with self.assertRaises(ValueError):
            JournalService.create_entry(
                tenant_id=str(self.org_1),
                entry_date=date(2026, 5, 20),
                description="Post en periodo cerrado",
                lines_data=lines
            )
