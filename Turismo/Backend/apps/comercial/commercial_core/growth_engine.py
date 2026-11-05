import logging
from ..models import Subscription, Plan, UsageMetric, AddOn

logger = logging.getLogger(__name__)

class GrowthEngine:
    """
    Motor de Upsell / Cross-sell (Crecimiento Inteligente).
    Identifica oportunidades de expansión.
    """

    @staticmethod
    def evaluate_upsell_opportunities(subscription: Subscription):
        """
        Evalúa si el tenant necesita un plan superior o add-ons.
        """
        plan = subscription.plan

        # 1. Verificar límites de almacenamiento
        # (Lógica simplificada usando la última métrica)
        latest_storage = UsageMetric.objects.filter(
            tenant_id=subscription.tenant_id,
            metric_type='STORAGE'
        ).order_by('-period_end').first()

        if latest_storage and latest_storage.quantity > (plan.storage_limit_gb * 0.9):
            GrowthEngine.suggest_upgrade(subscription, "STORAGE_LIMIT_NEAR")

    @staticmethod
    def suggest_upgrade(subscription: Subscription, reason: str):
        logger.info(f"CRECIMIENTO: Sugiriendo upgrade para {subscription.tenant_id} por {reason}")
        # Enviar notificación de sistema o email comercial
        pass
