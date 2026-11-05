from decimal import Decimal
from django.db.models import Sum, Avg
from ..models import Subscription, Plan

class RevenueMetrics:
    """
    Calcula KPIs financieros de SaaS.
    """

    @staticmethod
    def calculate_mrr():
        active_subs = Subscription.objects.filter(status=Subscription.Status.ACTIVE).select_related('plan')
        mrr = Decimal('0.00')
        for sub in active_subs:
            if sub.billing_cycle == Subscription.BillingCycle.MONTHLY:
                mrr += sub.plan.monthly_price
            else:
                mrr += sub.plan.monthly_price # Asumiendo que monthly_price es el valor base mensual aunque se pague anual
        return mrr

    @staticmethod
    def calculate_arr():
        return RevenueMetrics.calculate_mrr() * 12

    @staticmethod
    def calculate_arpu():
        """Average Revenue Per User (Tenant)."""
        mrr = RevenueMetrics.calculate_mrr()
        active_count = Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()
        if active_count == 0: return Decimal('0.00')
        return mrr / active_count

    @staticmethod
    def calculate_ltv(churn_rate):
        """Lifetime Value."""
        arpu = RevenueMetrics.calculate_arpu()
        if churn_rate == 0: return Decimal('0.00')
        return arpu / Decimal(str(churn_rate / 100))
