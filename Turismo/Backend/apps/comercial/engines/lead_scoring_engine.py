import logging
from ..models import Lead

logger = logging.getLogger(__name__)

class LeadScoringEngine:
    """
    Motor encargado de calificar la calidad de los prospectos (leads).
    """

    @staticmethod
    def calculate_score(lead: Lead) -> dict:
        """
        Calcula el puntaje basado en industria, tamaño y origen.
        """
        score = 0

        # 1. Tamaño de la empresa
        size_weights = {
            'ENTERPRISE': 40,
            'MEDIUM': 25,
            'SMALL': 10,
            'STARTUP': 15
        }
        score += size_weights.get(lead.company_size.upper(), 0)

        # 2. Industria Prioritaria
        priority_industries = ['TURISMO', 'HOTELERIA', 'VIAJES', 'TECNOLOGIA']
        if lead.industry.upper() in priority_industries:
            score += 20

        # 3. Origen
        if lead.source.lower() in ['ads', 'referral']:
            score += 15

        # 4. Valor estimado
        if lead.estimated_value > 5000:
            score += 25

        final_score = min(score, 100)

        classification = 'COLD'
        if final_score >= 75:
            classification = 'HOT'
        elif final_score >= 40:
            classification = 'WARM'

        return {
            'score': final_score,
            'classification': classification
        }

    @staticmethod
    def update_lead(lead: Lead):
        results = LeadScoringEngine.calculate_score(lead)
        lead.score = results['score']
        lead.save()
        return results
