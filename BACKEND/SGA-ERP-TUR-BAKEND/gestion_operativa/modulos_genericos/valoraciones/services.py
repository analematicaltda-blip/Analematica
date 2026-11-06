import logging
logger = logging.getLogger(__name__)
class ValoracionService:
    @staticmethod
    def log_feedback(resena_id):
        logger.info(f"Procesando feedback para reseña {resena_id}")
