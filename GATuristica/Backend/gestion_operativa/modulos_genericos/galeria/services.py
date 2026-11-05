import logging
logger = logging.getLogger(__name__)
class GaleriaService:
    @staticmethod
    def upload_image(perfil_id, image_data):
        logger.info(f"Imagen subida para perfil {perfil_id}")
