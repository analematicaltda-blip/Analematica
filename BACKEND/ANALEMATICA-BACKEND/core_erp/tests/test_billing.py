from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.core_erp.billing_engine import BillingEngine
from unittest.mock import MagicMock

class BillingEngineTest(TestCase):
    def test_calculate_totals(self):
        invoice = MagicMock()
        item1 = MagicMock(subtotal=Decimal('100.00'), tax_amount=Decimal('19.00'))
        item2 = MagicMock(subtotal=Decimal('50.00'), tax_amount=Decimal('0.00'))
        invoice.lines.all.return_value = [item1, item2]

        total = BillingEngine.calculate_totals(invoice)
        # 100 + 50 (subtotal) + 19 (tax) = 169
        self.assertEqual(total, Decimal('169.00'))
        self.assertEqual(invoice.total_amount, Decimal('169.00'))

    def test_validate_invoice_ok(self):
        invoice = MagicMock(number='FAC-001', total_amount=Decimal('100.00'))
        # Should not raise
        BillingEngine.validate_invoice(invoice)

    def test_validate_invoice_no_number(self):
        invoice = MagicMock(number='', total_amount=Decimal('100.00'))
        with self.assertRaises(ValidationError):
            BillingEngine.validate_invoice(invoice)
