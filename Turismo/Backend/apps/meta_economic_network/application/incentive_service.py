import logging
from decimal import Decimal
from django.db import transaction
from ..models import MetaEcosystem, GlobalUtilityMetric

logger = logging.getLogger(__name__)

class IncentiveMatrixService:
    """
    Incentive Alignment Matrix - Phase 20.5.
    Ajusta recompensas y penalizaciones basadas en el beneficio sistémico y riesgo inducido.
    """

    @staticmethod
    @transaction.atomic
    def evaluate_ecosystem_incentives(ecosystem_id):
        """
        Calcula el multiplicador de incentivos para un ecosistema específico.
        Factoriza: Contribución Marginal vs Riesgo Sistémico.
        """
        ecosystem = MetaEcosystem.objects.get(id=ecosystem_id)
        last_metric = ecosystem.utility_history.order_by('-timestamp').first()

        if not last_metric:
            return Decimal('1.0') # Neutral

        # Base Multiplier: (Contribution / (Externality + Penalty)) normalized
        denominator = last_metric.externality_cost + last_metric.risk_penalty
        if denominator > 0:
            performance_ratio = last_metric.contribution_score / denominator
        else:
            performance_ratio = Decimal('2.0') # Max benefit if no risks/costs

        # Clamping multiplier between 0.5 (Penalty) and 2.0 (Reward)
        multiplier = Decimal(str(max(min(performance_ratio, 2.0), 0.5))).quantize(Decimal('0.01'))

        logger.info(f"Incentive Matrix: Multiplier for {ecosystem.name} set to {multiplier}")

        # Integration with Phase 18 Economic Incentives
        IncentiveMatrixService._apply_meta_reward(ecosystem, multiplier)

        return multiplier

    @staticmethod
    def _apply_meta_reward(ecosystem, multiplier):
        """
        Emite recompensas tokenizadas o ajusta flujos de capital basados en el multiplicador.
        """
        if multiplier > 1.2:
            # High systemic benefit -> Grant Reward
            reward_value = ecosystem.economic_output * (multiplier - Decimal('1.0')) * Decimal('0.01')
            logger.info(f"Incentive Matrix: REWARD granted to {ecosystem.name}: {reward_value}")

            # Integration with economic_ecosystem or tokenization
            # Placeholder for cross-app service call
        elif multiplier < 0.8:
            # High systemic risk -> Apply Penalty (Flow Restriction)
            logger.warning(f"Incentive Matrix: PENALTY applied to {ecosystem.name} (Risk Restriction active)")
            ecosystem.is_active = False # Temporary decoupling if risk is too high
            ecosystem.save()

    @staticmethod
    def run_global_incentive_rebalance():
        """
        Rebalancea incentivos en toda la red meta-económica.
        """
        ecosystems = MetaEcosystem.objects.filter(is_active=True)
        results = {}
        for eco in ecosystems:
            results[eco.name] = IncentiveMatrixService.evaluate_ecosystem_incentives(eco.id)

        return results
