from decimal import Decimal
from ..models import Plan, Subscription, AddOn

class PricingEngine:
    """
    Calcula los costos de suscripción dinámicamente.
    """

    @staticmethod
    def calculate_subscription_total(subscription: Subscription, usage_metrics=None):
        """
        Calcula el monto total a facturar para el periodo.
        Incluye plan base, tiers de uso y add-ons.
        """
        plan = subscription.plan

        # 1. Precio Base
        total = plan.monthly_price if subscription.billing_cycle == Subscription.BillingCycle.MONTHLY else plan.yearly_price

        # 2. Add-ons
        for addon in subscription.add_ons.all():
            total += addon.monthly_price if subscription.billing_cycle == Subscription.BillingCycle.MONTHLY else addon.monthly_price * 12

        # 3. Escalonado (Tiers) por uso
        if plan.billing_schema == Plan.BillingSchema.TIERED and usage_metrics:
            for metric in usage_metrics:
                # Lógica simplificada de tiers
                tier = plan.tiers.filter(from_unit__lte=metric['quantity']).order_by('-from_unit').first()
                if tier:
                    total += tier.price_per_unit * Decimal(str(metric['quantity']))

        return total
