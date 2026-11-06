from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseInvoice
from apps.core_erp.event_bus import EventBus

@receiver(post_save, sender=PurchaseInvoice)
def request_purchase_financial_impact(sender, instance, created, **kwargs):
    if created and instance.status == 'APPROVED':
        payload = {
            "tenant_id": str(instance.tenant_id),
            "event_type": "PURCHASE_INVOICE_APPROVED",
            "date": str(instance.issue_date or instance.created_at.date()),
            "description": f"Purchase: {instance.supplier.name} - Inv {instance.number}",
            "reference": f"PUR-{instance.id}",
            "impacts": [
                {"account_code": "510101", "debit": str(instance.total_amount), "credit": "0.00"},
                {"account_code": "220501", "debit": "0.00", "credit": str(instance.total_amount)}
            ]
        }
        EventBus.emit("FINANCIAL_IMPACT_REQUESTED", payload)
