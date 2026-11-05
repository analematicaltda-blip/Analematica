from infrastructure.repositories.reservation_repository import ReservationRepository
import logging

logger = logging.getLogger(__name__)

class ReservationService:
    """
    Capa de Aplicación para gestión de reservas.
    Implementa reglas de negocio complejas y orquestación.
    """
    def __init__(self):
        self.repository = ReservationRepository()

    def process_cancellation(self, reservation_id):
        logger.info(f"ReservationService: Procesando cancelación de {reservation_id}")
        # Aquí se podrían añadir reglas como: "no cancelar si faltan menos de 24h"
        return self.repository.cancel(reservation_id)

    def process_validation(self, reservation_id):
        logger.info(f"ReservationService: Validando reserva {reservation_id}")
        # Bussines logic: Check for fraud or double booking before validation
        return self.repository.update_status(reservation_id, 'VALIDADA')

    def get_active_bookings_report(self):
        bookings = self.repository.list_active()
        return [
            {"id": str(b.id), "date": b.fecha.isoformat(), "provider": b.prestador.nombre_comercial}
            for b in bookings
        ]
