import logging
from django.dispatch import receiver
from .commercial_events import (
    subscription_activated, subscription_renewed,
    usage_limit_reached, payment_failed
)
from ..commercial_core.billing_adapter import BillingAdapter

logger = logging.getLogger(__name__)

@receiver(subscription_activated)
def handle_activation(sender, subscription, **kwargs):
    logger.info(f"EVENTO: Suscripción ACTIVADA para {subscription.tenant_id}")
    BillingAdapter.trigger_auto_billing(subscription)

@receiver(subscription_renewed)
def handle_renewal(sender, subscription, **kwargs):
    logger.info(f"EVENTO: Suscripción RENOVADA para {subscription.tenant_id}")
    BillingAdapter.trigger_auto_billing(subscription)

@receiver(usage_limit_reached)
def handle_limit(sender, subscription, metric_type, **kwargs):
    logger.warning(f"EVENTO: Límite de {metric_type} alcanzado para {subscription.tenant_id}")
    # Aquí se dispararía el motor de Upsell en el futuro

@receiver(payment_failed)
def handle_payment_failure(sender, subscription, reason, **kwargs):
    logger.error(f"EVENTO: Fallo de pago para {subscription.tenant_id}. Razón: {reason}")
    # Marcar como past_due
    from ..commercial_core.subscription_engine import SubscriptionEngine
    SubscriptionEngine.handle_past_due(subscription)
