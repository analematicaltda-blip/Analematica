import logging
from decimal import Decimal
from django.db import transaction
from apps.core_erp.event_bus import EventBus
from ..models.provider_models import TourismProvider, Reservation, TourismService

logger = logging.getLogger(__name__)

class TourismFinancialService:
    """
    Orquesta la integración financiera entre el Dominio Turismo y el Wallet.
    """

    @staticmethod
    @transaction.atomic
    def process_reservation_payment(reservation_id: str):
        """
        Ejecuta el pago de una reserva: de Turista a Prestador via EventBus.
        """
        reservation = Reservation.objects.get(id=reservation_id)
        if reservation.status != Reservation.Status.PENDING:
            raise ValueError("La reserva no está en estado pendiente para pago.")

        prestador_user = reservation.provider.owner

        payload = {
            "customer_id": str(reservation.customer.id),
            "target_user_id": str(prestador_user.id),
            "amount": float(reservation.total_price),
            "related_service_id": str(reservation.service.id),
            "description": f"Pago Reserva {reservation.id} - {reservation.service.name}",
            "reservation_id": str(reservation.id)
        }

        # Desacoplamiento via EventBus
        EventBus.emit('WALLET_PAYMENT_REQUESTED', payload)

        # Actualización optimista o via evento de respuesta
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save()

        return {"status": "payment_emitted", "reservation_id": reservation_id}

    @staticmethod
    def register_transaction(provider, amount, customer, description="Venta Directa"):
        """
        Registra una transacción directa sin reserva previa (POS).
        """
        payload = {
            "customer_id": str(customer.id),
            "target_user_id": str(provider.owner.id),
            "amount": float(amount),
            "description": description
        }
        EventBus.emit('WALLET_PAYMENT_REQUESTED', payload)
        return {"status": "payment_emitted"}

    @staticmethod
    def calculate_commission(amount, percentage=Decimal('0.10')):
        """
        Calcula la comisión para la plataforma.
        """
        return (amount * percentage).quantize(Decimal('0.01'))

    @staticmethod
    def get_provider_balance(provider_id: str):
        # En una arquitectura 100% desacoplada, el balance se consultaría
        # via API o mensaje síncrono. Aquí emitimos evento o usamos el servicio
        # de wallet si está en el mismo proceso, pero cumpliendo la directriz:
        # Por ahora devolvemos un placeholder que indica que debe consultarse via WalletDomain.
        return Decimal('0.00')
