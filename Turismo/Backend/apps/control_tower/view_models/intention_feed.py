from typing import List, Dict, Any
from apps.admin_plataforma.models import GovernanceIntention

class IntentionFeed:
    """
    ViewModel: Provides a real-time feed of governance intentions and their outcomes.
    """

    @staticmethod
    def get_recent_intentions(limit=20) -> List[Dict[str, Any]]:
        intentions = GovernanceIntention.objects.order_by('-timestamp')[:limit]
        return [
            {
                "id": str(i.id),
                "domain": i.origin_domain,
                "action": i.requested_action.get("intention"),
                "status": i.validation_status,
                "risk": i.risk_score,
                "timestamp": i.timestamp.isoformat()
            } for i in intentions
        ]
