from typing import Dict, Any
from apps.enterprise_core.models.risk_snapshot import RiskSnapshot

class SystemicRiskView:
    """
    ViewModel: Specialized view for the Risk Heatmap and simulation indicators.
    """

    @staticmethod
    def get_risk_context() -> Dict[str, Any]:
        latest = RiskSnapshot.objects.order_by('-timestamp').first()
        return {
            "overall_score": latest.overall_score if latest else 0.0,
            "factors": latest.risk_factors if latest else {},
            "status": "NORMAL" if (latest and latest.overall_score < 0.4) else "WARNING",
            "last_updated": latest.timestamp.isoformat() if latest else None
        }
