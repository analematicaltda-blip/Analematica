from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PayrollRun
from apps.core_erp.event_bus import EventBus
from apps.core_erp.contracts.financial_contract import JournalEntryDTO, JournalEntryLineDTO
from decimal import Decimal

@receiver(post_save, sender=PayrollRun)
def request_payroll_financial_impact(sender, instance, created, **kwargs):
    """
    Emits an event for financial impact instead of creating models directly.
    Achieves Domain Isolation (Stage 3).
    """
    if created:
        # Create DTO for the impact
        # Note: We still need to know which accounts to use, or the listener handles it.
        # Standard: Domain provides the 'intent' and 'amounts', Accounting handles the 'posting'.

        payload = {
            "tenant_id": str(instance.tenant_id),
            "event_type": "PAYROLL_RUN_FINALIZED",
            "date": str(instance.period_end or instance.created_at.date()),
            "description": f"Payroll Journal Entry: Period {instance.period_start} to {instance.period_end}",
            "reference": f"PAYROLL-RUN-{instance.id}",
            "impacts": [
                {"account_code": "510506", "debit": str(instance.total_earnings), "credit": "0.00"},
                {"account_code": "250501", "debit": "0.00", "credit": str(instance.net_total)},
                {"account_code": "237005", "debit": "0.00", "credit": str(instance.total_deductions)}
            ]
        }

        EventBus.emit("FINANCIAL_IMPACT_REQUESTED", payload)
