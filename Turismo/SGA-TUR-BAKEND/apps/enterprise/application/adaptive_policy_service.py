import logging
from decimal import Decimal
from apps.core_erp.event_bus import EventBus
from ..domain.policy import EnterprisePolicy
from ..domain.autonomous import AutonomousActionRecord
from apps.control_tower.domain.alert import Alert

logger = logging.getLogger(__name__)

class AdaptivePolicyService:
    """
    Autonomous Policy Engine (Phase 9).
    Executes actions based on autonomy levels and optimizes thresholds.
    """

    @staticmethod
    def execute_policy(tenant_id, value, policy, correlation_id):
        """
        Executes policy action according to its autonomy level.
        Levels 0-5.
        """
        level = policy.autonomy_level
        action = policy.action_on_breach

        logger.info(f"EOS Autonomous: Executing policy {policy.name} at Level {level}")

        # Level 0: Only Alert
        if level == 0:
            AdaptivePolicyService._trigger_alert(tenant_id, value, policy)

        # Level 1: Recommend (Handled by creating a proposal in the system)
        elif level == 1:
            AdaptivePolicyService._create_recommendation(tenant_id, value, policy)

        # Level 2: Execute with Confirmation
        elif level == 2:
            AdaptivePolicyService._request_execution_approval(tenant_id, value, policy)

        # Level 3: Auto-Execute within boundaries
        elif level >= 3:
            AdaptivePolicyService._auto_execute_action(tenant_id, value, policy, correlation_id)

        # Level 5: Strategic Optimization (Adjusts other policies)
        if level == 5:
            AdaptivePolicyService._optimize_strategy(tenant_id, policy)

    @staticmethod
    def _trigger_alert(tenant_id, value, policy):
        Alert.objects.create(
            tenant_id=tenant_id,
            severity='CRITICAL',
            title=f"Autonomous Alert: {policy.name}",
            description=f"Policy breach detected: {value} vs threshold {policy.threshold}.",
            entity_scope=policy.scope
        )

    @staticmethod
    def _auto_execute_action(tenant_id, value, policy, correlation_id):
        # 1. Dispatch Event for execution
        EventBus.emit("AUTONOMOUS_ACTION_TRIGGERED", {
            "tenant_id": str(tenant_id),
            "policy_id": str(policy.id),
            "action": policy.action_on_breach,
            "params": policy.action_params
        })

        # 2. Audit Record
        AutonomousActionRecord.objects.create(
            tenant_id=tenant_id,
            policy=policy,
            autonomy_level=policy.autonomy_level,
            execution_payload={"metric_value": str(value), "params": policy.action_params},
            outcome_status="EXECUTED",
            correlation_id=correlation_id
        )
        logger.warning(f"EOS Autonomous: ACTION EXECUTED AUTOMATICALLY for {policy.name}")

    @staticmethod
    def _optimize_strategy(tenant_id, policy):
        """
        Level 5 logic: The system adjusts its own strategic parameters.
        """
        # Implementation for self-tuning of the policy thresholds
        pass
