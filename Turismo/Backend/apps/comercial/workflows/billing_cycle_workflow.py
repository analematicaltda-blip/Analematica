from django.utils import timezone
from ..models import Subscription
from ..services.subscription_service import SubscriptionService

class BillingCycleWorkflow:
    """
    Workflow para el procesamiento masivo de facturación mensual.
    """

    @staticmethod
    def process_monthly_billing():
        active_subs = Subscription.objects.filter(status=Subscription.Status.ACTIVE)
        results = {"processed": 0, "failed": 0}

        for sub in active_subs:
            try:
                SubscriptionService.renew_subscription(sub.id)
                results["processed"] += 1
            except Exception:
                results["failed"] += 1
        return results
