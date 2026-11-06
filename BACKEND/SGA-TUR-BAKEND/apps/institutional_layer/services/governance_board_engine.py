import logging
from django.utils import timezone
from ..models import BoardDecision

logger = logging.getLogger(__name__)

class GovernanceBoardEngine:
    """
    Motor de Gobernanza Corporativa Digital (Fase 7).
    """

    @staticmethod
    def propose_decision(committee, title, description, user, simulation_data=None):
        decision = BoardDecision.objects.create(
            committee=committee,
            title=title,
            description=description,
            proposed_by=user,
            impact_simulation=simulation_data
        )
        logger.info(f"BOARD: Decisión propuesta en comité {committee}: {title}")
        return decision

    @staticmethod
    def approve_decision(decision_id):
        decision = BoardDecision.objects.get(id=decision_id)
        decision.status = BoardDecision.Status.APPROVED
        decision.finalized_at = timezone.now()
        decision.save()

        # Auditoría institucional automática
        from .audit_trail_engine import AuditTrailEngine
        AuditTrailEngine.log_critical_change(
            user=decision.proposed_by,
            action=f"BOARD_APPROVAL_{decision.committee}",
            financial_impact=0,
            details={"decision_title": decision.title, "id": str(decision.id)}
        )

        return decision

    @staticmethod
    def get_board_minutes():
        """
        Genera un historial formal de decisiones tipo Acta.
        """
        return BoardDecision.objects.filter(status=BoardDecision.Status.APPROVED).order_by('-finalized_at')
