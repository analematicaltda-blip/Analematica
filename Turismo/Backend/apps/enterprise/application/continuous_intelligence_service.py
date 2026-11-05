import logging
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from ..domain.autonomous import LearningLoopRecord
from ..domain.policy import EnterprisePolicy
from apps.control_tower.domain.kpi import KPI

logger = logging.getLogger(__name__)

class ContinuousIntelligenceService:
    """
    Learning Loop Layer (Phase 9).
    Analyzes historical trends to suggest policy optimizations.
    """

    @staticmethod
    def run_learning_cycle(tenant_id):
        """
        Runs analysis to optimize financial and operational boundaries.
        """
        # Example: Analyze EBITDA Margin Stability
        target_metric = "EBITDA_MARGIN"

        # 1. Fetch historical trend (last 30 days)
        history = KPI.objects.filter(
            tenant_id=tenant_id,
            name=target_metric,
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).values_list('value', flat=True)

        if not history: return

        avg_metric = sum(history) / len(history)
        volatility = max(history) - min(history)

        # 2. Suggest Threshold Adjustment if volatility is low
        policy = EnterprisePolicy.objects.filter(tenant_id=tenant_id, metric_name=target_metric).first()
        if policy and volatility < (avg_metric * Decimal('0.05')):
            # If stable, we can tighten the threshold to detect smaller deviations
            suggested_threshold = avg_metric * Decimal('0.95') # Tighten to 5% variance

            record = LearningLoopRecord.objects.create(
                tenant_id=tenant_id,
                engine_name="STABILITY_OPTIMIZER",
                input_trend_data={"avg": str(avg_metric), "volatility": str(volatility)},
                previous_rule_state={"threshold": str(policy.threshold)},
                suggested_rule_state={"threshold": str(suggested_threshold)},
                confidence_level=Decimal('0.8500')
            )

            logger.info(f"EOS Learning: Optimization suggested for {target_metric}")

            # Level 4 Autonomy: Auto-apply rule adjustments
            if policy.autonomy_level >= 4:
                policy.threshold = suggested_threshold
                policy.save()
                record.is_applied = True
                record.applied_at = timezone.now()
                record.save()
                logger.warning(f"EOS Learning: RULE AUTO-ADJUSTED for {target_metric}")
