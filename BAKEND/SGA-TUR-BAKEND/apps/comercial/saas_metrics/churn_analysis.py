from ..models import Subscription
from django.utils import timezone
from datetime import timedelta

class ChurnAnalysis:
    """
    Analiza la tasa de cancelación y salud de tenants.
    """

    @staticmethod
    def calculate_churn_rate(days=30):
        """
        Tasa de churn en los últimos X días.
        """
        start_date = timezone.now().date() - timedelta(days=days)
        canceled_count = Subscription.objects.filter(
            status=Subscription.Status.CANCELED,
            end_date__gte=start_date
        ).count()

        total_active_at_start = Subscription.objects.filter(
            is_active=True
        ).count() + canceled_count

        if total_active_at_start == 0: return 0.0
        return (canceled_count / total_active_at_start) * 100
