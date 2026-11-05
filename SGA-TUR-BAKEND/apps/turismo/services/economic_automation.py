import logging
from apps.tourism_intelligence.analytics_engine import ConversationalAnalyticsEngine
from apps.tourism_intelligence.models import ConversationalIntent
from apps.turismo.models.provider_models import TourismService, TourismProvider
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class EconomicAutomationService:
    """
    Vía 4: Automatización Económica.
    Convierte intenciones (Vía 3) en sugerencias de transacciones (Vía 5).
    """

    @staticmethod
    def process_intent_for_automation(intent: ConversationalIntent):
        """
        Analiza una intención y dispara acciones automatizadas de recomendación o reserva.
        """
        if intent.intent == ConversationalIntent.IntentType.SEARCH_HOTEL:
            EconomicAutomationService._suggest_accommodation(intent)
        elif intent.intent == ConversationalIntent.IntentType.SEARCH_FOOD:
            EconomicAutomationService._suggest_restaurant(intent)
        elif intent.intent == ConversationalIntent.IntentType.BOOKING_REQUEST:
            EconomicAutomationService._trigger_booking_workflow(intent)

    @staticmethod
    def _suggest_accommodation(intent: ConversationalIntent):
        """
        Busca alojamientos disponibles y envía recomendación.
        """
        services = TourismService.objects.filter(
            service_type=TourismService.ServiceType.ACCOMMODATION,
            availability=True
        )[:3]

        # Simulación de respuesta de recomendación vía Social App
        logger.info(f"Vía 4: Sugiriendo {services.count()} alojamientos al turista {intent.tourist.username}")

        for svc in services:
             # Emitir evento de recomendación económica
             EventBus.emit('ECONOMIC_RECOMMENDATION_SENT', {
                 'user_id': str(intent.tourist.id),
                 'service_id': str(svc.id),
                 'price': float(svc.price),
                 'reason': 'Conversational Intent: SEARCH_HOTEL'
             })

    @staticmethod
    def _suggest_restaurant(intent: ConversationalIntent):
        """
        Busca restaurantes y envía recomendación.
        """
        services = TourismService.objects.filter(
            service_type=TourismService.ServiceType.FOOD,
            availability=True
        )[:3]

        logger.info(f"Vía 4: Sugiriendo {services.count()} opciones gastronómicas")

    @staticmethod
    def _trigger_booking_workflow(intent: ConversationalIntent):
        """
        Detecta que el usuario quiere reservar y ofrece el botón de pago rápido.
        """
        # Si el usuario mencionó un precio o servicio previo, podríamos pre-armar la reserva
        logger.info(f"Vía 4: Disparando flujo de reserva inmediata para {intent.tourist.username}")

        EventBus.emit('BOOKING_FLOW_TRIGGERED', {
            'user_id': str(intent.tourist.id),
            'intent_id': str(intent.id)
        })
