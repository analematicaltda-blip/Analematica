from apps.core_erp.event_bus import EventBus
from .decision_engine import DecisionEngine
from .risk_engine import RiskEngine

def register_decision_handlers():
    EventBus.subscribe("KPI_UPDATED", handle_kpi_for_decisions)
    EventBus.subscribe("PERIOD_CLOSED", handle_period_closed_risk)

def handle_kpi_for_decisions(payload):
    DecisionEngine.evaluate_metrics(payload.get('tenant_id'), {payload.get('name'): payload.get('value')})

def handle_period_closed_risk(payload):
    RiskEngine.evaluate_all_risks(payload.get('tenant_id'))
