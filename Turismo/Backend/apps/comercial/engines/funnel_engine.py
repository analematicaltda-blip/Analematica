import logging
from ..models import Opportunity
from ..models import Lead

logger = logging.getLogger(__name__)

class FunnelEngine:
    """
    Motor de gestión del embudo de ventas.
    """

    @staticmethod
    def create_opportunity(lead: Lead, expected_plan: str, estimated_revenue: float) -> Opportunity:
        if lead.status == Lead.Status.REJECTED:
             raise ValueError("No se puede crear oportunidad para un lead rechazado.")

        opportunity = Opportunity.objects.create(
            lead=lead,
            expected_plan=expected_plan,
            estimated_revenue=estimated_revenue,
            stage=Opportunity.Stage.PROSPECTING,
            probability=10
        )
        return opportunity

    @staticmethod
    def transition_stage(opportunity: Opportunity, new_stage: str):
        old_stage = opportunity.stage
        opportunity.stage = new_stage

        stage_probabilities = {
            Opportunity.Stage.PROSPECTING: 10,
            Opportunity.Stage.PROPOSAL: 30,
            Opportunity.Stage.NEGOTIATION: 60,
            Opportunity.Stage.WON: 100,
            Opportunity.Stage.LOST: 0
        }
        opportunity.probability = stage_probabilities.get(new_stage, opportunity.probability)
        opportunity.save()

        if new_stage == Opportunity.Stage.WON:
             opportunity.lead.status = Lead.Status.CONVERTED
             opportunity.lead.save()

        return opportunity
