from apps.comercial.models import Subscription, Plan
from django.db.models import Sum, Avg, Count, Q

class GrowthPatterns:
    """
    Detecta patrones de expansión y segmentos de alto valor.
    """

    @staticmethod
    def analyze_segments():
        """
        Analiza qué tipos de usuarios generan mayor LTV.
        """
        return Subscription.objects.values('plan__target_user_type').annotate(
            avg_mrr=Avg('plan__monthly_price'),
            count=Count('id')
        ).order_by('-avg_mrr')

    @staticmethod
    def get_best_performing_plans():
        """
        Identifica planes con menor tasa de cancelación histórica.
        """
        return Plan.objects.filter(is_active=True).annotate(
            active_subscriptions=Count('subscription', filter=Q(subscription__status='ACTIVE')),
            total_historical=Count('subscription')
        )
