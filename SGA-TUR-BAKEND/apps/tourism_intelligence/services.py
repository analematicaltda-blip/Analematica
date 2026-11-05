import logging
from decimal import Decimal
from django.db.models import Sum, Avg
from .models import TourismDemandForecast, TourismSeasonality, TouristBehaviorProfile, TourismEconomicImpact
from apps.turismo.models.provider_models import TourismService, Reservation

logger = logging.getLogger(__name__)

class TourismIntelligenceService:
    """
    Motor Central de Inteligencia Turística SARITA.
    """

    @staticmethod
    def generate_economic_report(destino, periodo):
        """
        Calcula el impacto económico real basado en transacciones de Wallet y Ledger.
        """
        reservas = Reservation.objects.filter(
            status=Reservation.Status.COMPLETED,
            provider__location__icontains=destino # Filtro simplificado por ubicación
        )

        total_ventas = reservas.aggregate(Sum('total_price'))['total_price__sum'] or 0

        impact, created = TourismEconomicImpact.objects.update_or_create(
            destino=destino,
            periodo=periodo,
            defaults={
                'ventas_totales': total_ventas,
                'ingresos_turisticos_netos': total_ventas * Decimal('0.90'), # Descontando comisión
                'empleo_generado_estimado': int(len(reservas) / 10) # Ratio hipotético
            }
        )
        return impact

    @staticmethod
    def predict_demand(destino, categoria, fecha):
        """
        Calcula la demanda estimada basada en tendencias históricas.
        """
        # En una fase real, aquí se llamaría a un modelo de ML (SADI-AI)
        # Mock de predicción inteligente:
        demanda_base = Reservation.objects.filter(service__service_type=categoria).count()
        prediction = demanda_base * 1.15 # Proyección de crecimiento del 15%

        forecast, _ = TourismDemandForecast.objects.update_or_create(
            destino=destino,
            categoria_servicio=categoria,
            fecha=fecha,
            defaults={'demanda_estimada': int(prediction)}
        )
        return forecast

class DynamicPricingService:
    """
    Motor de Precios Dinámicos para optimización de conversión.
    """

    @staticmethod
    def get_suggested_price(service_id):
        """
        Sugiere un ajuste de precio según demanda y ocupación.
        """
        service = TourismService.objects.get(id=service_id)
        base_price = service.price

        # 1. Ajuste por temporada (Seasonality)
        current_month = 3 # Marzo por ejemplo
        season = TourismSeasonality.objects.filter(mes=current_month).first()

        multiplier = 1.0
        if season:
            if season.nivel_demanda == TourismSeasonality.DemandLevel.HIGH:
                multiplier = 1.20
            elif season.nivel_demanda == TourismSeasonality.DemandLevel.LOW:
                multiplier = 0.85

        suggested_price = base_price * Decimal(str(multiplier))

        return {
            "service": service.name,
            "base_price": base_price,
            "suggested_price": suggested_price.quantize(Decimal('0.01')),
            "adjustment_reason": "Alta Demanda Estacional" if multiplier > 1 else "Optimización de Ocupación"
        }
