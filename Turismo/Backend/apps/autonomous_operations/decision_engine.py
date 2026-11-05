import logging
from .models import AutonomousAgent, DecisionProposal, AgentExecutionAudit
from apps.operational_intelligence.models import SaaSMetric, ChurnRiskScore, UnitEconomics
from decimal import Decimal

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Generates strategic proposals based on operational data.
    """

    @staticmethod
    def run_all_agents():
        agents = AutonomousAgent.objects.filter(status='ACTIVE')
        for agent in agents:
            DecisionEngine.run_agent(agent)

    @staticmethod
    def run_agent(agent: AutonomousAgent):
        if agent.domain == 'churn':
            DecisionEngine._handle_churn_domain(agent)
        elif agent.domain == 'pricing':
            DecisionEngine._handle_pricing_domain(agent)

        agent.last_execution = Decimal('0.00') # Placeholder for performance calc
        # Update last execution time
        from django.utils import timezone
        agent.last_execution = timezone.now()
        agent.save()

    @staticmethod
    def _handle_churn_domain(agent):
        # 1. Look for HIGH risk customers from Churn Engine (Phase 5)
        high_risk = ChurnRiskScore.objects.filter(risk_level='HIGH')

        for risk in high_risk:
            # Check if we already have a pending proposal for this customer
            if DecisionProposal.objects.filter(target_entity_id=risk.customer_id, status='PENDING').exists():
                continue

            # Propose a preventive discount
            DecisionProposal.objects.create(
                agent=agent,
                target_entity_id=risk.customer_id,
                target_entity_type='CUSTOMER',
                proposed_action='APPLY_PREVENTIVE_DISCOUNT',
                action_parameters={'discount_rate': 0.10, 'duration_months': 3},
                expected_impact={'churn_reduction_probability': 0.65},
                confidence_score=Decimal('75.00')
            )

            AgentExecutionAudit.objects.create(
                agent_code=agent.agent_code,
                step='DECISION',
                data={'customer_id': str(risk.customer_id), 'action': 'DISCOUNT'}
            )

    @staticmethod
    def _handle_pricing_domain(agent):
        # 1. Look for low margin customers from Unit Economics (Phase 5)
        low_margin = UnitEconomics.objects.filter(gross_margin__lt=15)

        for econ in low_margin:
            if DecisionProposal.objects.filter(target_entity_id=econ.customer_id, status='PENDING').exists():
                continue

            # Propose a price tier adjustment
            DecisionProposal.objects.create(
                agent=agent,
                target_entity_id=econ.customer_id,
                target_entity_type='CUSTOMER',
                proposed_action='ADJUST_USAGE_TIER',
                action_parameters={'increase_rate': 0.20},
                expected_impact={'margin_improvement': 10.0},
                confidence_score=Decimal('85.00')
            )
