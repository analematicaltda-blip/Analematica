import logging
from .models import AutonomousAction, AgentExecutionAudit
from apps.operational_intelligence.models import SaaSMetric
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger(__name__)

class LearningLoop:
    """
    Measures action impact and updates agent performance scores.
    """

    @staticmethod
    def run_feedback_cycle():
        # Look for actions executed 7+ days ago (to have enough data)
        # For Phase 6 demo, we'll look at recent actions too
        recent_actions = AutonomousAction.objects.filter(is_reverted=False)

        for action in recent_actions:
            LearningLoop.measure_impact(action)

    @staticmethod
    def measure_impact(action: AutonomousAction):
        proposal = action.proposal
        agent = proposal.agent

        # 1. Collect real result (Simulated logic for Phase 6)
        # In production: compare churn status or margin change 30 days later
        real_impact = 1.0 # Positive outcome

        # If customer churned anyway despite discount
        # real_impact = -1.0

        # 2. Update Performance Score
        # Simple moving average adjustment
        current_score = agent.performance_score
        adjustment = Decimal(str(real_impact)) * Decimal('5.0') # +5 points for success

        agent.performance_score = max(Decimal('0.00'), min(Decimal('100.00'), current_score + adjustment))
        agent.save()

        AgentExecutionAudit.objects.create(
            agent_code=agent.agent_code,
            step='LEARNING',
            related_id=action.id,
            data={'prev_score': float(current_score), 'new_score': float(agent.performance_score)}
        )

        return True
