import logging
logger = logging.getLogger(__name__)
class SargentoHorarios:
    @staticmethod
    def validar_turno(perfil_id, fecha, hora):
        logger.info(f"SARGENTO: Validando turno {fecha} {hora}")
        return True
