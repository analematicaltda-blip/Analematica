import logging
from django.utils import timezone
from apps.admin_plataforma.models import DecisionHistory

logger = logging.getLogger(__name__)

class ReinforcementEngine:
    """
    Motor de Aprendizaje por Refuerzo (Fase 5).
    Analiza el impacto de decisiones pasadas para optimizar parámetros futuros.
    """

    @staticmethod
    def record_outcome(decision_id, reward, impact_data=None):
        """
        Registra el resultado real de una decisión tomada por la IA.
        reward: float (-1.0 a 1.0)
        """
        try:
            decision = DecisionHistory.objects.get(id=decision_id)
            # Enriquecemos el registro de decisión con el impacto real
            if not hasattr(decision, 'metadata'):
                decision.metadata = {}

            decision.metadata['impact_reward'] = reward
            decision.metadata['impact_data'] = impact_data or {}
            decision.metadata['impact_recorded_at'] = timezone.now().isoformat()
            decision.save()

            logger.info(f"RL_ENGINE: Registrado impacto para decisión {decision_id}. Reward: {reward}")
        except DecisionHistory.DoesNotExist:
            logger.error(f"RL_ENGINE: No se encontró la decisión {decision_id}")

    @staticmethod
    def get_parameter_adjustment(parameter_name, current_value):
        """
        Sugiere un ajuste basado en el éxito histórico.
        Lógica simplificada: Si las decisiones recientes con valores altos tuvieron éxito, subir.
        """
        recent_decisions = DecisionHistory.objects.filter(
            intention__contains=parameter_name,
            timestamp__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-timestamp')[:50]

        if not recent_decisions:
            return current_value

        # Cálculo de tendencia de éxito
        positive_impacts = [d for d in recent_decisions if d.metadata.get('impact_reward', 0) > 0.5]
        negative_impacts = [d for d in recent_decisions if d.metadata.get('impact_reward', 0) < -0.2]

        if len(positive_impacts) > len(negative_impacts) * 2:
            return current_value * 1.05 # Optimismo: subir 5%
        elif len(negative_impacts) > len(positive_impacts):
            return current_value * 0.95 # Cautela: bajar 5%

        return current_value
