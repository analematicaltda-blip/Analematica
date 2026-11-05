import logging
from .models import Reserva
logger = logging.getLogger(__name__)
class ReservaService:
    @staticmethod
    def create_reserva(perfil_id, data):
        reserva = Reserva.objects.create(perfil_ref_id=perfil_id, **data)
        logger.info(f"Reserva creada: {reserva.id_publico}")
        return reserva
