from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DepreciationCalculation
from apps.core_erp.event_bus import EventBus

@receiver(post_save, sender=DepreciationCalculation)
def request_depreciation_financial_impact(sender, instance, created, **kwargs):
    if created:
        payload = {
            "tenant_id": str(instance.tenant_id),
            "event_type": "ASSET_DEPRECIATION_CALCULATED",
            "date": str(instance.calculation_date),
            "description": f"Depreciation: {instance.asset.name} - {instance.calculation_date}",
            "reference": f"DEP-{instance.asset.id}-{instance.id}",
            "impacts": [
                {"account_code": "516005", "debit": str(instance.amount), "credit": "0.00"},
                {"account_code": "159205", "debit": "0.00", "credit": str(instance.amount)}
            ]
        }
        EventBus.emit("FINANCIAL_IMPACT_REQUESTED", payload)
