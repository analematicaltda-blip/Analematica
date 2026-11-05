import logging
logger = logging.getLogger(__name__)
class SargentoValoraciones:
    @staticmethod
    def registrar_puntuacion(resena_id, puntos):
        logger.info(f"SARGENTO: Registrando {puntos} puntos para reseña {resena_id}")
