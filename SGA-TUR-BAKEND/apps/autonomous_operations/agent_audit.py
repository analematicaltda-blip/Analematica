from .models import AgentExecutionAudit
import logging

logger = logging.getLogger(__name__)

class AgentAudit:
    """
    Provides traceability services for autonomous actions.
    """

    @staticmethod
    def get_lifecycle_for_proposal(proposal_id):
        return AgentExecutionAudit.objects.filter(related_id=proposal_id).order_by('timestamp')

    @staticmethod
    def get_agent_history(agent_code):
        return AgentExecutionAudit.objects.filter(agent_code=agent_code).order_by('-timestamp')
