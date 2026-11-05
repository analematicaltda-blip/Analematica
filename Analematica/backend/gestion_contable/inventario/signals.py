from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InventoryMovement
from apps.core_erp.event_bus import EventBus
from decimal import Decimal

@receiver(post_save, sender=InventoryMovement)
def request_inventory_financial_impact(sender, instance, created, **kwargs):
    if created:
        amount = instance.quantity * instance.product.unit_price
        impacts = []

        if instance.movement_type == 'IN':
            impacts = [
                {"account_code": "143505", "debit": str(amount), "credit": "0.00"},
                # Assuming balancing account for simplified flow
                {"account_code": "220501", "debit": "0.00", "credit": str(amount)}
            ]
        elif instance.movement_type == 'OUT':
            impacts = [
                {"account_code": "613505", "debit": str(amount), "credit": "0.00"},
                {"account_code": "143505", "debit": "0.00", "credit": str(amount)}
            ]

        if impacts:
            payload = {
                "tenant_id": str(instance.tenant_id),
                "event_type": "INVENTORY_MOVEMENT_RECORDED",
                "date": str(instance.created_at.date() if instance.created_at else ""),
                "description": f"Inventory Movement: {instance.product.name} - {instance.movement_type}",
                "reference": f"INV-{instance.id}",
                "impacts": impacts
            }
            EventBus.emit("FINANCIAL_IMPACT_REQUESTED", payload)
