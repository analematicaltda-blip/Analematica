import logging
from .models import PolicyRule, DecisionProposal
from apps.core_erp.event_bus import EventBus
from decimal import Decimal

logger = logging.getLogger(__name__)

class PolicyEngine:
    """
    Governance layer to validate autonomous actions.
    """

    @staticmethod
    def initialize_default_policies():
        policies = [
            {
                'code': 'max-discount-limit',
                'description': 'Limits the maximum preventive discount to 15%',
                'parameters': {'max_discount': 0.15}
            },
            {
                'code': 'min-gross-margin',
                'description': 'Ensures actions do not drop gross margin below 10%',
                'parameters': {'min_margin': 0.10}
            },
            {
                'code': 'enterprise-protection',
                'description': 'Blocks automatic changes to enterprise accounts',
                'parameters': {'block_enterprise': True}
            }
        ]

        for p_data in policies:
            PolicyRule.objects.get_or_create(
                code=p_data['code'],
                defaults=p_data
            )
        logger.info("AUTONOMOUS OPERATIONS: Default policies initialized.")

    @staticmethod
    def validate_proposal(proposal: DecisionProposal):
        """
        Validates a proposal against all active policy rules.
        Returns (is_valid, reason)
        """
        rules = PolicyRule.objects.filter(is_active=True)

        for rule in rules:
            valid, reason = PolicyEngine._check_rule(rule, proposal)
            if not valid:
                proposal.status = 'BLOCKED'
                proposal.processing_notes = f"Blocked by policy {rule.code}: {reason}"
                proposal.save()

                EventBus.emit('AUTONOMOUS_ACTION_BLOCKED', {
                    'proposal_id': str(proposal.id),
                    'agent_code': proposal.agent.agent_code,
                    'policy_code': rule.code,
                    'reason': reason
                })
                return False, reason

        return True, "Passed all policies"

    @staticmethod
    def _check_rule(rule, proposal):
        params = rule.parameters

        if rule.code == 'max-discount-limit':
            discount = proposal.action_parameters.get('discount_rate', 0)
            if Decimal(str(discount)) > Decimal(str(params.get('max_discount'))):
                return False, f"Discount {discount} exceeds limit {params.get('max_discount')}"

        if rule.code == 'min-gross-margin':
            expected_margin = proposal.expected_impact.get('new_gross_margin', 1.0)
            if Decimal(str(expected_margin)) < Decimal(str(params.get('min_margin'))):
                return False, f"Expected margin {expected_margin} below safety threshold {params.get('min_margin')}"

        if rule.code == 'enterprise-protection':
            is_enterprise = proposal.action_parameters.get('is_enterprise', False)
            if is_enterprise and params.get('block_enterprise'):
                return False, "Cannot automatically modify enterprise accounts"

        return True, ""
