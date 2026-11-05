import logging
from django.db import transaction
from apps.core_erp.event_bus import EventBus
from ..models.provider_models import TourismProvider, Reservation, TourismService

logger = logging.getLogger(__name__)

class TourismDeliveryService:
    """
    Orquesta la integración logística entre el Dominio Turismo y el Delivery.
    """

    @staticmethod
    @transaction.atomic
    def request_delivery_for_reservation(reservation_id: str, origin_address: str, destination_address: str):
        reservation = Reservation.objects.get(id=reservation_id)

        if not reservation.service.delivery_available:
            raise ValueError(f"El servicio {reservation.service.name} no tiene delivery disponible.")

        parameters = {
            "user_id": str(reservation.customer.id),
            "origin_address": origin_address,
            "destination_address": destination_address,
            "estimated_price": 5000,
            "value_declared": float(reservation.total_price),
            "related_operational_order_id": str(reservation.id),
            "provider_id": str(reservation.provider.id),
            "items": [
                {
                    "description": f"Servicio Turístico: {reservation.service.name}",
                    "quantity": 1,
                    "weight_kg": 1.0
                }
            ]
        }

        # Desacoplamiento via EventBus
        EventBus.emit('DELIVERY_REQUESTED_FROM_TURISMO', parameters)

        # La vinculación se hará via evento de respuesta o ID en payload
        return {"status": "request_emitted", "reservation_id": reservation_id}

    @staticmethod
    def create_delivery(provider, customer, items, address):
        """
        Crea un pedido de delivery directo.
        """
        parameters = {
            "user_id": str(customer.id),
            "origin_address": "Sede Prestador",
            "destination_address": address,
            "provider_id": str(provider.id),
            "items": items
        }
        EventBus.emit('DELIVERY_REQUESTED_DIRECT', parameters)
        return {"status": "request_emitted"}
