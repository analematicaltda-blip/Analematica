import logging
from .models import Reservation

logger = logging.getLogger(__name__)

class DomainSargentoReservas:
    """
    Consolidated logic for Reservations.
    """
    @staticmethod
    def confirm_reservation(reservation_id):
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save()
        logger.info(f"DOMAIN SARGENTO: Reservation {reservation_id} confirmed.")
