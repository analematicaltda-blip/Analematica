import logging
from decimal import Decimal
from ..domain.decision_engine import EnterpriseDecisionRule
from ..domain.logs import DecisionLog
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Automated Decision Engine of EOS.
    Translates metric triggers into recommended or automated actions.
    """

    @staticmethod
    def evaluate_metrics(tenant_id, metrics_payload):
        """
        Processes incoming metrics and checks against decision rules.
        """
        for metric_name, value in metrics_payload.items():
            rules = EnterpriseDecisionRule.objects.filter(
                trigger_metric=metric_name,
                is_active=True
            )

            for rule in rules:
                if DecisionEngine._condition_met(value, rule):
                    DecisionEngine._process_decision(tenant_id, value, rule)

    @staticmethod
    def _condition_met(value, rule):
        val = Decimal(str(value))
        if rule.condition == 'LT': return val < rule.threshold
        if rule.condition == 'GT': return val > rule.threshold
        if rule.condition == 'LTE': return val <= rule.threshold
        if rule.condition == 'GTE': return val >= rule.threshold
        return False

    @staticmethod
    def _process_decision(tenant_id, value, rule):
        logger.info(f"EOS Decision: Rule triggered for metric {rule.trigger_metric}")

        # 1. Recommendation
        recommendation = f"RECOMMEND: {rule.recommended_action} due to {rule.trigger_metric} = {value}"

        # 2. Execution (if auto_execute enabled)
        execution_result = "PENDING_APPROVAL"
        if rule.auto_execute:
            execution_result = DecisionEngine._execute_action(tenant_id, rule)

        # 3. Log the decision in the Data Lake layer
        DecisionLog.objects.create(
            tenant_id=tenant_id,
            decision_type="RULE_BASED_DECISION",
            input_payload={"metric": rule.trigger_metric, "value": str(value)},
            output_result={"action": rule.recommended_action, "status": execution_result},
            actor_id="EOS_DECISION_ENGINE",
            reasoning=f"Automatic evaluation of rule {rule.id}"
        )

    @staticmethod
    def _execute_action(tenant_id, rule):
        """
        Executes the specific action mapped to the rule.
        """
        logger.warning(f"EOS EXECUTION: Executing '{rule.recommended_action}' for tenant {tenant_id}")

        # Dispatch to EventBus to trigger actions in other domains
        EventBus.emit("EOS_DECISION_EXECUTED", {
            "tenant_id": str(tenant_id),
            "action": rule.recommended_action,
            "rule_id": str(rule.id)
        })

        return "EXECUTED"
