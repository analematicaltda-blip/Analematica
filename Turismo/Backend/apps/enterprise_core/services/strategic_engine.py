import logging
from typing import Dict, Any, List
from ..models.strategic_rule import StrategicRule

logger = logging.getLogger(__name__)

class StrategicEngine:
    """
    Core logic for evaluating strategic rules.
    Part of the Strategic Rule Engine layer.
    """

    @staticmethod
    def get_matching_rules(metric_name: str, value: Any) -> List[StrategicRule]:
        # Usar plain_objects para evitar filtros de tenant en este contexto global si aplica
        active_rules = StrategicRule.plain_objects.filter(trigger_metric=metric_name, is_active=True)
        matching = []
        for rule in active_rules:
            if StrategicEngine._evaluate_condition(rule.condition_expression, value):
                matching.append(rule)
        return matching

    @staticmethod
    def _evaluate_condition(expression: str, value: Any) -> bool:
        """
        Safe expression parser for strategic conditions.
        """
        try:
            parts = expression.split()
            if len(parts) != 3 or parts[0] != 'metric':
                return False

            operator = parts[1]
            threshold = float(parts[2])
            metric_val = float(value)

            if operator == '<': return metric_val < threshold
            if operator == '>': return metric_val > threshold
            if operator == '<=': return metric_val <= threshold
            if operator == '>=': return metric_val >= threshold
            if operator == '==': return metric_val == threshold
            if operator == '!=': return metric_val != threshold

            return False
        except Exception:
            return False
