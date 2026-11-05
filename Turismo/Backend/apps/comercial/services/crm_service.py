import logging
from ..models import Lead
from ..engines.lead_scoring_engine import LeadScoringEngine
from ..engines.funnel_engine import FunnelEngine

logger = logging.getLogger(__name__)

class CRMService:
    """
    Servicio de alto nivel para la gestión de relaciones con clientes.
    """

    @staticmethod
    def register_new_lead(data: dict) -> Lead:
        lead = Lead.objects.create(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            source=data.get('source', 'organic'),
            industry=data.get('industry', ''),
            company_size=data.get('company_size', 'SMALL'),
            estimated_value=data.get('estimated_value', 0)
        )
        LeadScoringEngine.update_lead(lead)
        if lead.score >= 75:
            FunnelEngine.create_opportunity(
                lead=lead,
                expected_plan=data.get('target_plan', 'BASIC'),
                estimated_revenue=float(lead.estimated_value)
            )
        return lead

    @staticmethod
    def get_sales_pipeline_stats():
        return {
            "total_leads": Lead.objects.count(),
            "leads_by_status": {
                "new": Lead.objects.filter(status=Lead.Status.NEW).count(),
                "qualified": Lead.objects.filter(status=Lead.Status.QUALIFIED).count(),
                "converted": Lead.objects.filter(status=Lead.Status.CONVERTED).count()
            }
        }
