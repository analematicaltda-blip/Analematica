from decimal import Decimal
from apps.comercial.models import Subscription

class PricingSimulator:
    """
    Simula cambios en el esquema de precios y su impacto.
    """

    @staticmethod
    def simulate_price_increase(percentage_increase):
        active_subs = Subscription.objects.filter(status=Subscription.Status.ACTIVE)

        current_revenue = Decimal('0.00')
        simulated_revenue = Decimal('0.00')

        factor = Decimal('1') + (Decimal(str(percentage_increase)) / 100)

        for sub in active_subs:
            price = sub.plan.monthly_price
            current_revenue += price
            simulated_revenue += price * factor

        return {
            "current_mrr": current_revenue,
            "simulated_mrr": simulated_revenue,
            "impact": simulated_revenue - current_revenue
        }
