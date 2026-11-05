from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.core_erp.accounting_engine import AccountingEngine
from unittest.mock import MagicMock

class AccountingEngineTest(TestCase):
    """
    Pruebas para el motor contable del Core ERP.
    """

    def test_validate_balance_correct(self):
        # Mock de un asiento con transacciones balanceadas
        entry = MagicMock()
        t1 = MagicMock(debit=Decimal('100.00'), credit=Decimal('0.00'))
        t2 = MagicMock(debit=Decimal('0.00'), credit=Decimal('100.00'))
        entry.lines.all.return_value = [t1, t2]
        del entry.transactions

        self.assertTrue(AccountingEngine.validate_balance(entry))

    def test_validate_balance_incorrect(self):
        # Mock de un asiento descuadrado
        entry = MagicMock()
        t1 = MagicMock(debit=Decimal('100.00'), credit=Decimal('0.00'))
        t2 = MagicMock(debit=Decimal('0.00'), credit=Decimal('50.00'))
        entry.lines.all.return_value = [t1, t2]
        del entry.transactions

        with self.assertRaises(ValidationError):
            AccountingEngine.validate_balance(entry)

    def test_post_entry_already_posted(self):
        entry = MagicMock(is_posted=True)
        with self.assertRaises(ValidationError):
            AccountingEngine.post_journal_entry(entry)

    def test_validate_balance_complex(self):
        entry = MagicMock()
        t1 = MagicMock(debit=Decimal('100.00'), credit=Decimal('0.00'))
        t2 = MagicMock(debit=Decimal('0.00'), credit=Decimal('60.00'))
        t3 = MagicMock(debit=Decimal('0.00'), credit=Decimal('40.00'))
        entry.lines.all.return_value = [t1, t2, t3]
        del entry.transactions

        self.assertTrue(AccountingEngine.validate_balance(entry))
