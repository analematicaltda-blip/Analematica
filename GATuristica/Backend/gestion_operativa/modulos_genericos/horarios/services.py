import logging
logger = logging.getLogger(__name__)
class HorarioService:
    @staticmethod
    def check_availability(perfil_id, date, time):
        logger.info(f"Verificando disponibilidad para {date} {time}")
        return True
