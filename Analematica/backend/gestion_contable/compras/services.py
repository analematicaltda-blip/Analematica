import logging
import csv
import io
from decimal import Decimal
from django.utils import timezone
from .models import PurchaseInvoice, Supplier
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class ProcurementService:
    """
    Enterprise-grade service for Procurement and Supplier Management.
    Restores and enhances legacy payment features.
    """

    @staticmethod
    def generate_massive_payment_file(tenant_id, invoice_ids):
        """
        Generates a standardized CSV for banking portals.
        Restores legacy functionality.
        """
        invoices = PurchaseInvoice.objects.filter(tenant_id=tenant_id, id__in=invoice_ids)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Supplier Name', 'Tax ID', 'Invoice Number', 'Amount', 'Currency'])

        total_amount = Decimal('0.00')
        for inv in invoices:
            writer.writerow([
                inv.supplier.name,
                inv.supplier.tax_id,
                inv.number,
                inv.total_amount,
                inv.currency
            ])
            total_amount += inv.total_amount

        logger.info(f"Procurement: Generated massive payment file for {invoices.count()} invoices (Total: {total_amount})")
        return output.getvalue()

    @staticmethod
    def process_supplier_payment(tenant_id, invoice_id, amount, bank_reference):
        """
        Records a payment and emits events for financial impact.
        """
        invoice = PurchaseInvoice.objects.get(tenant_id=tenant_id, id=invoice_id)

        # 1. Update status
        invoice.status = 'PAID'
        invoice.save()

        # 2. Emit Financial Impact
        payload = {
            "tenant_id": str(tenant_id),
            "event_type": "SUPPLIER_PAYMENT_PROCESSED",
            "date": str(timezone.now().date()),
            "description": f"Payment for Invoice {invoice.number} - Ref: {bank_reference}",
            "reference": bank_reference,
            "impacts": [
                {"account_code": "220501", "debit": str(amount), "credit": "0.00"}, # Reduce Payable
                {"account_code": "111005", "debit": "0.00", "credit": str(amount)}  # Reduce Bank
            ]
        }
        EventBus.emit("FINANCIAL_IMPACT_REQUESTED", payload)

        return invoice
