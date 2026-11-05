from django.utils import timezone
from datetime import timedelta
from apps.comercial.models import Subscription, UsageMetric, BillingCycle
from django.db.models import Avg, Sum, Count

class FeatureExtractor:
    """
    Extrae señales del ecosistema para alimentar modelos predictivos.
    """

    @staticmethod
    def get_tenant_features(tenant_id):
        subscription = Subscription.objects.get(tenant_id=tenant_id)
        now = timezone.now().date()

        # 1. Uso de recursos (últimos 30 días)
        usage_avg = UsageMetric.objects.filter(
            tenant_id=tenant_id,
            period_end__gte=now - timedelta(days=30)
        ).aggregate(avg_qty=Avg('quantity'))['avg_qty'] or 0

        # 2. Comportamiento de Pago
        failed_payments = BillingCycle.objects.filter(
            subscription=subscription,
            status='failed'
        ).count()

        # 3. Tendencia de actividad (Actividad hoy vs promedio)
        last_activity_days = (timezone.now() - subscription.last_activity).days if subscription.last_activity else 99

        return {
            "usage_intensity": float(usage_avg),
            "payment_friction": failed_payments,
            "inactivity_period": last_activity_days,
            "health_score": subscription.health_score
        }
