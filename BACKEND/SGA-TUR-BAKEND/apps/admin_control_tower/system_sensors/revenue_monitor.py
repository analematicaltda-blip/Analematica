from decimal import Decimal
from django.db.models import Sum
from apps.admin_plataforma.gestion_contable.contabilidad.models import AdminAccountingTransaction
from apps.comercial.models import Subscription

class RevenueMonitor:
    """
    Monitor especializado en la salud comercial del Holding.
    """

    @staticmethod
    def get_revenue_by_plan():
        """
        Desglosa ingresos por tipo de plan.
        """
        return Subscription.objects.filter(
            status=Subscription.Status.ACTIVE
        ).values('plan__name').annotate(
            total_revenue=Sum('plan__monthly_price')
        )

    @staticmethod
    def calculate_churn_rate():
        """
        Calcula la tasa de cancelación (simplificado).
        """
        canceled = Subscription.objects.filter(status=Subscription.Status.CANCELED).count()
        total = Subscription.objects.count()
        if total == 0: return 0.0
        return (canceled / total) * 100
