import logging
from apps.core_erp.event_bus import EventBus
from .lead_model import SaaSLead

logger = logging.getLogger(__name__)

class LeadScoringEngine:
    """
    Asigna puntaje automático a los Leads SaaS basado en factores estratégicos.
    """
    QUALIFICATION_THRESHOLD = 50

    # Configuración de Pesos
    WEIGHTS = {
        'industry_multiplier': {
            'Software': 1.5,
            'Fintech': 1.4,
            'Hotel': 1.3,
            'Restaurant': 1.1,
            'Other': 1.0
        },
        'size_points': 5, # Puntos por cada unidad de estimated_size (ej: empleados)
        'utm_bonus': 10,  # Bonus por venir de campañas pagas específicas
        'demo_bonus': 30,
    }

    @classmethod
    def process_lead(cls, lead: SaaSLead, metadata: dict = None) -> int:
        """
        Calcula y actualiza el score de un lead.
        """
        metadata = metadata or {}
        score = 0

        # 1. Scoring por Tamaño (Estimated Size)
        score += lead.estimated_size * cls.WEIGHTS['size_points']

        # 2. Multiplicador por Industria
        multiplier = cls.WEIGHTS['industry_multiplier'].get(lead.industry, cls.WEIGHTS['industry_multiplier']['Other'])
        score = int(score * multiplier)

        # 3. Bonus por Origen UTM
        if lead.utm_source in ['google_ads', 'linkedin_ads']:
            score += cls.WEIGHTS['utm_bonus']

        # 4. Interacción (Demo)
        if metadata.get('demo_requested'):
            score += cls.WEIGHTS['demo_bonus']

        # Actualizar Lead
        lead.score = score

        # Evaluar Calificación
        if lead.score >= cls.QUALIFICATION_THRESHOLD and lead.status == SaaSLead.Status.NEW:
            lead.status = SaaSLead.Status.QUALIFIED
            lead.save()
            logger.info(f"LEAD QUALIFIED: {lead.company_name} (Score: {lead.score})")
            EventBus.emit('LEAD_QUALIFIED', {
                'lead_id': str(lead.id),
                'company_name': lead.company_name,
                'score': lead.score
            })
        else:
            lead.save()

        return score
