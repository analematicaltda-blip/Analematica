import logging
from decimal import Decimal
from apps.core_erp.event_bus import EventBus
from ..domain.policy import EnterprisePolicy
from apps.control_tower.domain.alert import Alert

logger = logging.getLogger(__name__)

class PolicyEvaluationService:
    """
    Evaluates corporate policies against system metrics.
    """

    @staticmethod
    def register_handlers():
        """
        Listens to KPI updates from the Control Tower.
        """
        # Note: Control Tower doesn't emit a KPI_UPDATED event yet, but it should.
        # For Phase D, we'll assume an event is emitted after MonitoringService calculates KPIs.
        EventBus.subscribe("KPI_UPDATED", PolicyEvaluationService.handle_kpi_update)
        logger.info("Enterprise Policy Engine registered.")

    @staticmethod
    def handle_kpi_update(payload):
        """
        Triggered when a KPI is updated.
        """
        tenant_id = payload.get('tenant_id')
        metric_name = payload.get('name')
        value = Decimal(str(payload.get('value', 0)))

        # 1. Find active policies for this metric and scope
        policies = EnterprisePolicy.objects.filter(
            metric_name=metric_name,
            is_active=True
        )

        from ..domain.logs import PolicyEvaluationLog
        for policy in policies:
            is_breached = PolicyEvaluationService._check_breach(value, policy)

            # Log evaluation
            PolicyEvaluationLog.objects.create(
                tenant_id=tenant_id,
                policy=policy,
                metric_value=value,
                was_breached=is_breached,
                action_taken=policy.action_on_breach if is_breached else "NONE"
            )

            if is_breached:
                from .adaptive_policy_service import AdaptivePolicyService
                AdaptivePolicyService.execute_policy(tenant_id, value, policy, payload.get('correlation_id'))

    @staticmethod
    def _check_breach(value, policy):
        if policy.operator == 'GT': return value > policy.threshold
        if policy.operator == 'LT': return value < policy.threshold
        if policy.operator == 'GTE': return value >= policy.threshold
        if policy.operator == 'LTE': return value <= policy.threshold
        if policy.operator == 'EQ': return value == policy.threshold
        return False

    @staticmethod
    def _execute_policy_action(tenant_id, value, policy):
        logger.warning(f"POLICY BREACH: Policy {policy.name} violated by value {value}")

        if policy.action_on_breach == EnterprisePolicy.Action.ALERT:
            Alert.objects.create(
                tenant_id=tenant_id,
                severity='CRITICAL',
                title=f"Corporate Policy Breach: {policy.name}",
                description=f"Metric {policy.metric_name} value {value} violated policy threshold {policy.threshold}.",
                entity_scope=policy.scope
            )

        elif policy.action_on_breach == EnterprisePolicy.Action.ESCALATE:
            # Logic for escalation to CFO or senior management
            pass

        elif policy.action_on_breach == EnterprisePolicy.Action.WORKFLOW:
            # Trigger a corrective EnterpriseWorkflow
            workflow_id = policy.action_params.get('workflow_id')
            if workflow_id:
                # OrchestrationService.trigger(workflow_id, ...)
                pass
