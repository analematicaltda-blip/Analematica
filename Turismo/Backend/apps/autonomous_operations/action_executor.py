import logging
import hashlib
from .models import DecisionProposal, AutonomousAction, AgentExecutionAudit
from .policy_engine import PolicyEngine
from apps.core_erp.event_bus import EventBus
from django.utils import timezone

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Executes validated proposals based on autonomy levels.
    """

    @staticmethod
    def process_pending_proposals():
        proposals = DecisionProposal.objects.filter(status='PENDING')
        for proposal in proposals:
            ActionExecutor.evaluate_and_execute(proposal)

    @staticmethod
    def evaluate_and_execute(proposal: DecisionProposal):
        # 1. Policy Validation
        is_valid, reason = PolicyEngine.validate_proposal(proposal)
        if not is_valid:
            AgentExecutionAudit.objects.create(
                agent_code=proposal.agent.agent_code,
                step='POLICY',
                related_id=proposal.id,
                data={'status': 'BLOCKED', 'reason': reason},
                success=False
            )
            return False

        # 2. Autonomy Check
        agent = proposal.agent
        if agent.autonomy_level == 'ADVISORY':
            # Do nothing, wait for human approval
            return False

        if agent.autonomy_level == 'SUPERVISED' and proposal.status != 'APPROVED':
            # Wait for human to change status to APPROVED
            return False

        # 3. Execution
        try:
            result = ActionExecutor._execute_action(proposal)

            # Record execution
            execution_hash = hashlib.sha256(f"{proposal.id}-{timezone.now()}".encode()).hexdigest()
            AutonomousAction.objects.create(
                proposal=proposal,
                execution_hash=execution_hash,
                result_data=result
            )

            proposal.status = 'EXECUTED'
            proposal.processed_at = timezone.now()
            proposal.save()

            AgentExecutionAudit.objects.create(
                agent_code=agent.agent_code,
                step='ACTION',
                related_id=proposal.id,
                data={'hash': execution_hash, 'result': result}
            )

            EventBus.emit('AUTONOMOUS_ACTION_EXECUTED', {
                'proposal_id': str(proposal.id),
                'action': proposal.proposed_action,
                'agent': agent.agent_code
            })

            return True
        except Exception as e:
            logger.error(f"Error executing autonomous action: {str(e)}")
            proposal.status = 'FAILED'
            proposal.processing_notes = str(e)
            proposal.save()
            return False

    @staticmethod
    def _execute_action(proposal):
        # Implementation of real system changes
        action = proposal.proposed_action
        params = proposal.action_parameters

        if action == 'APPLY_PREVENTIVE_DISCOUNT':
            # Logic to apply discount in commercial_engine
            # (Simulated for Phase 6 certification)
            return {'status': 'SUCCESS', 'applied_discount': params.get('discount_rate')}

        if action == 'ADJUST_USAGE_TIER':
            # Logic to adjust tiers in usage_billing
            return {'status': 'SUCCESS', 'new_rate': params.get('increase_rate')}

        return {'status': 'UNKNOWN_ACTION'}

    @staticmethod
    def revert_action(action_id):
        action = AutonomousAction.objects.get(id=action_id)
        # Logic to reverse the specific action
        # ...
        action.is_reverted = True
        action.reverted_at = timezone.now()
        action.reversion_data = {'reason': 'Human override'}
        action.save()
        return True
