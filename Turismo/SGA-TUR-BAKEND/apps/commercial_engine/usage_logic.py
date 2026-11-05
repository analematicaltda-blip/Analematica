from django.db import models
from .models import SaaSSubscription, UsageEvent, UsageAggregation

class SaaSUsageBillingEngine:
    """
    Motor de facturación basado en uso.
    """

    @staticmethod
    def aggregate_usage(tenant_id, metric_type, start_date, end_date):
        total = UsageEvent.objects.filter(
            tenant_id=tenant_id,
            metric_type=metric_type,
            timestamp__date__range=[start_date, end_date]
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

        return total

    @staticmethod
    def calculate_usage_charge(subscription, metric_type, quantity):
        # Lógica de precios por unidad (pueden venir del plan)
        unit_price = 0.01 # Placeholder
        return quantity * unit_price
