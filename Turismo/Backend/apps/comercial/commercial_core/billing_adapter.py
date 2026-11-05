import logging
from ..engines.billing_engine import BillingEngine
from .pricing_engine import PricingEngine

logger = logging.getLogger(__name__)

class BillingAdapter:
    """
    Adapta el ciclo de vida comercial al motor de facturación ERP.
    """

    @staticmethod
    def trigger_auto_billing(subscription):
        """
        Disparado por eventos de renovación.
        """
        total = PricingEngine.calculate_subscription_total(subscription)

        # Delegar al motor de facturación que ya tiene el impacto contable
        invoice = BillingEngine.generate_invoice(subscription)

        logger.info(f"Facturación automática completada para {subscription.tenant_id}")
        return invoice
