import logging
from django.db.models import Avg, Count
from .models import ProviderReputation, TourismReview, ProductRanking, TourismConversionMetrics
from apps.turismo.models.provider_models import TourismService

logger = logging.getLogger(__name__)

class TourismRecommendationService:
    """
    Motor de Recomendación Inteligente para el Marketplace SARITA.
    """

    @staticmethod
    def get_personalized_recommendations(user, limit=5):
        """
        Genera recomendaciones basadas en popularidad y ranking sistémico.
        """
        # Priorizar servicios con mayor score total
        top_services = TourismService.objects.filter(
            is_active=True,
            availability=True,
            ranking__score_total__gt=0
        ).select_related('ranking', 'provider').order_by('-ranking__score_total')[:limit]

        return top_services

    @staticmethod
    def get_trending_services(limit=5):
        """
        Servicios con mayor actividad económica reciente.
        """
        return TourismService.objects.filter(
            is_active=True
        ).order_by('-conversion_metrics__reservas')[:limit]

    @staticmethod
    def update_product_rankings():
        """
        Ejecuta el recálculo masivo de scores para el algoritmo de descubrimiento.
        """
        services = TourismService.objects.all()
        for service in services:
            ranking, _ = ProductRanking.objects.get_or_create(service=service)

            # Reputación (de la tabla Reputation)
            reputation = ProviderReputation.objects.filter(provider=service.provider).first()
            if reputation:
                ranking.indice_reputacion = reputation.indice_confiabilidad

            # Popularidad (basada en reservas)
            metrics = TourismConversionMetrics.objects.filter(service=service).first()
            if metrics:
                ranking.indice_popularidad = min(metrics.reservas / 100, 1.0) # Normalizado
                ranking.indice_conversion = metrics.conversion_rate / 100

            ranking.calculate_total_score()

        logger.info("MARKETPLACE: Rankings actualizados exitosamente.")
