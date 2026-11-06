import logging
from apps.core_erp.event_bus import EventBus
from .services import DeliveryLogisticService
from api.models import CustomUser

logger = logging.getLogger(__name__)

class DeliveryEventHandlers:
    """
    Manejadores de eventos para el dominio de Delivery.
    Permite que otros dominios soliciten servicios logísticos sin importación directa.
    """

    @staticmethod
    def handle_delivery_request(payload: dict):
        """
        Procesa una solicitud de delivery proveniente de otro dominio (Ej: Turismo).
        """
        user_id = payload.get('user_id')
        user = CustomUser.objects.filter(id=user_id).first()

        logistic_service = DeliveryLogisticService(user=user)
        try:
            service_record = logistic_service.create_request(payload)
            logger.info(f"Delivery: Solicitud procesada exitosamente ID {service_record.id}")
        except Exception as e:
            logger.error(f"Delivery: Error al procesar solicitud externa: {e}")

    @staticmethod
    def register_all():
        """
        Registra los suscriptores en el EventBus.
        """
        EventBus.subscribe('DELIVERY_REQUESTED_FROM_TURISMO', DeliveryEventHandlers.handle_delivery_request)
        EventBus.subscribe('DELIVERY_REQUESTED_DIRECT', DeliveryEventHandlers.handle_delivery_request)
        logger.info("Delivery Event Handlers registrados.")
