import logging
from decimal import Decimal
from typing import Dict, Any
from ..models.decision_proposal import DecisionProposal
from .strategic_engine import StrategicEngine
from ..integration.governance_adapter import GovernanceAdapter
from apps.core_erp.event_bus import EventBus
from django.db import transaction

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Main Orchestrator for Enterprise EOS decisions.
    Integrates all layers from intake to execution.
    """

    @staticmethod
    def process_metric_update(metric_name: str, value: Any, context: Dict[str, Any] = None):
        logger.info(f"DecisionEngine: Processing metric {metric_name} with value {value}")
        rules = StrategicEngine.get_matching_rules(metric_name, value)
        logger.info(f"DecisionEngine: Found {len(rules)} matching rules.")

        for rule in rules:
            DecisionEngine._generate_proposal(rule, value, context)

    @staticmethod
    def _generate_proposal(rule, current_value, context):
        with transaction.atomic():
            proposal = DecisionProposal.objects.create(
                origin_metric=rule.trigger_metric,
                metric_value=current_value,
                evaluated_risk=rule.risk_weight,
                suggested_action={
                    "intention": rule.recommended_action,
                    "parameters": context or {}
                },
                autonomy_level_applied=rule.autonomy_level,
                policy_reference=str(rule.id),
                tenant_id=rule.tenant_id
            )

            # Notify System
            EventBus.emit("STRATEGIC_PROPOSAL_GENERATED", {
                "proposal_id": str(proposal.id),
                "action": rule.recommended_action,
                "autonomy_level": rule.autonomy_level
            })

            # Phase 5: Autonomous Execution Logic
            should_auto_execute = False

            if rule.autonomy_level == 3:
                should_auto_execute = True
            elif rule.autonomy_level == 2:
                # Check impact threshold (Example logic: context contains estimated impact)
                estimated_impact = Decimal(str(context.get('estimated_impact', 0))) if context else 0
                if estimated_impact <= rule.impact_threshold:
                    should_auto_execute = True
                else:
                    logger.warning(f"Proposal {proposal.id} exceeds threshold for auto-execution.")
                    EventBus.emit("EXECUTIVE_ESCALATION_REQUIRED", {
                        "proposal_id": str(proposal.id),
                        "impact": float(estimated_impact),
                        "threshold": float(rule.impact_threshold)
                    }, severity="warning")

            if should_auto_execute:
                DecisionEngine.execute_proposal(proposal.id, auto=True)

    @staticmethod
    def execute_proposal(proposal_id, user=None, auto=False):
        proposal = DecisionProposal.objects.get(id=proposal_id)
        if proposal.executed:
            return {"status": "ALREADY_EXECUTED"}

        # Phase 5: Executing Agent Metadata
        execution_context = proposal.suggested_action.get("parameters", {})
        execution_context["_agent_id"] = proposal.agent_id
        execution_context["_autonomy_level"] = proposal.autonomy_level_applied
        execution_context["_policy_ref"] = proposal.policy_reference

        # Validate via Governance Validation Layer
        result = GovernanceAdapter.validate_and_execute(
            proposal.suggested_action["intention"],
            execution_context,
            user=user
        )

        proposal.executed = True
        proposal.governance_status = DecisionProposal.Status.EXECUTED
        proposal.execution_result = result
        proposal.save()

        # Emit Real-time audit event for Tower of Control
        EventBus.emit("AUTONOMOUS_DECISION_EXECUTED", {
            "proposal_id": str(proposal.id),
            "agent": proposal.agent_id,
            "action": proposal.suggested_action["intention"],
            "status": "SUCCESS" if result.get("status") == "SUCCESS" else "FAILED"
        }, severity="info")

        return result
