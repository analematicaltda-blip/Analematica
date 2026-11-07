from decimal import Decimal
from ..models import UsageMetric
from ..models import Subscription

class MonetizationService:
    """
    Servicio para calcular cargos basados en el uso.
    """

    @staticmethod
    def record_usage(tenant_id, metric_type, quantity, period_start, period_end):
        return UsageMetric.objects.create(
            tenant_id=tenant_id,
            metric_type=metric_type,
            quantity=quantity,
            period_start=period_start,
            period_end=period_end
        )

    @staticmethod
    def calculate_overage(subscription: Subscription):
        # La lógica real está en el BillingEngine
        return Decimal('0.00')
