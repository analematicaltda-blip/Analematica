import logging
from django.utils import timezone
from datetime import timedelta
from ..models import Subscription

logger = logging.getLogger(__name__)

class RetentionEngine:
    """
    Motor de Retención Automática (Fase 3).
    Detecta riesgos de churn y activa contramedidas.
    """

    @staticmethod
    def analyze_health(subscription: Subscription):
        """
        Analiza la salud de una suscripción basada en actividad reciente.
        """
        now = timezone.now()

        # 1. Verificar inactividad
        if subscription.last_activity:
            days_inactive = (now - subscription.last_activity).days
            if days_inactive > 15:
                subscription.health_score = 0.4 # Riesgo Crítico
            elif days_inactive > 7:
                subscription.health_score = 0.7 # Riesgo Moderado
        else:
            subscription.health_score = 0.5 # Nunca ha tenido actividad

        subscription.save()

        if subscription.health_score < 0.5:
            RetentionEngine.trigger_retention_campaign(subscription)

    @staticmethod
    def trigger_retention_campaign(subscription: Subscription):
        """
        Dispara acciones automáticas de retención.
        """
        logger.warning(f"RETENCIÓN: Activando campaña para {subscription.tenant_id}")
        # En implementación real: Enviar email, ofrecer cupón, alertar a soporte
        pass
