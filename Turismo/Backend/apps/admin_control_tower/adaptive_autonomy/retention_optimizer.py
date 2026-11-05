import logging
from apps.comercial.models import Subscription
from .reinforcement_engine import ReinforcementEngine

logger = logging.getLogger(__name__)

class RetentionOptimizer:
    """
    Optimizador de Retención (Fase 5).
    Selecciona la intervención óptima para prevenir el churn.
    """

    STRATEGIES = [
        'AUTOMATIC_DISCOUNT',
        'TEMPORARY_UPGRADE',
        'PRIORITY_SUPPORT_ASSIGNMENT',
        'TRIAL_EXTENSION'
    ]

    @staticmethod
    def select_optimal_intervention(tenant_id):
        """
        Determina qué estrategia tiene mayor probabilidad de éxito para este tenant.
        """
        # Obtenemos tasas de éxito históricas por estrategia
        success_rates = {}
        for strategy in RetentionOptimizer.STRATEGIES:
            # Consultamos al RL Engine por el éxito de esta estrategia
            adjustment_factor = ReinforcementEngine.get_parameter_adjustment(strategy, 1.0)
            success_rates[strategy] = adjustment_factor

        # Seleccionamos la de mejor performance (Exploitation)
        best_strategy = max(success_rates, key=success_rates.get)

        logger.info(f"RETENTION_OPT: Seleccionada estrategia '{best_strategy}' para {tenant_id}")
        return best_strategy

    @staticmethod
    def record_retention_success(tenant_id, strategy, was_retained):
        """
        Informa al RL Engine sobre el resultado de una intervención.
        """
        reward = 1.0 if was_retained else -0.5
        # En una implementación real vinculamos con el decision_id generado al ejecutar la intervención
        pass
        # ReinforcementEngine.record_outcome(decision_id, reward)
