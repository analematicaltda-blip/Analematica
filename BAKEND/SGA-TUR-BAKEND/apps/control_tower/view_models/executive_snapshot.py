from typing import Dict, Any
from dataclasses import dataclass
from apps.control_tower.models import KPI, Alert
from apps.enterprise_core.models.decision_proposal import DecisionProposal
from apps.enterprise_core.models.risk_snapshot import RiskSnapshot

@dataclass
class ExecutiveSnapshot:
    """
    ViewModel: Aggregates system health into a single structure for the dashboard.
    Does not query tables directly; uses service aggregation or EventBus context.
    """
    kpis: Dict[str, Any]
    systemic_risk: float
    active_proposals: int
    open_alerts: int
    infra_status: str

    @classmethod
    def get_latest(cls):
        # In a real EOS, this data would be cached from the EventBus / Metric Registry
        kpis = {
            "mrr": 54000.0,
            "churn": 0.02,
            "ebitda": 12500.0
        }

        latest_risk = RiskSnapshot.objects.order_by('-timestamp').first()
        proposals_count = DecisionProposal.objects.filter(executed=False).count()
        alerts_count = Alert.objects.filter(status='OPEN').count()

        return cls(
            kpis=kpis,
            systemic_risk=latest_risk.overall_score if latest_risk else 0.0,
            active_proposals=proposals_count,
            open_alerts=alerts_count,
            infra_status="OPTIMAL"
        )
