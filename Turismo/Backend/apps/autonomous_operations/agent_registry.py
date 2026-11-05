import logging
from .models import AutonomousAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Manages the lifecycle of autonomous agents.
    """

    @staticmethod
    def register_default_agents():
        agents = [
            {
                'agent_code': 'pricing-optimizer',
                'name': 'Pricing Strategy Agent',
                'domain': 'pricing',
                'autonomy_level': 'ADVISORY',
                'risk_level': 'MEDIUM'
            },
            {
                'agent_code': 'churn-prevention',
                'name': 'Retention Specialist Agent',
                'domain': 'churn',
                'autonomy_level': 'ADVISORY',
                'risk_level': 'LOW'
            },
            {
                'agent_code': 'marketing-autobot',
                'name': 'Marketing Budget Agent',
                'domain': 'marketing',
                'autonomy_level': 'ADVISORY',
                'risk_level': 'MEDIUM'
            },
            {
                'agent_code': 'cashflow-guardian',
                'name': 'Liquidity Guardian Agent',
                'domain': 'cashflow',
                'autonomy_level': 'ADVISORY',
                'risk_level': 'HIGH'
            }
        ]

        for agent_data in agents:
            AutonomousAgent.objects.get_or_create(
                agent_code=agent_data['agent_code'],
                defaults=agent_data
            )
        logger.info("AUTONOMOUS OPERATIONS: Default agents registered.")

    @staticmethod
    def set_autonomy(agent_code, level):
        agent = AutonomousAgent.objects.get(agent_code=agent_code)
        agent.autonomy_level = level
        agent.save()
        return agent
