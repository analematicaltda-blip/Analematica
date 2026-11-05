import logging
logger = logging.getLogger(__name__)
class SargentoGaleria:
    @staticmethod
    def registrar_imagen(perfil_id, url):
        logger.info(f"SARGENTO: Registrando imagen en galería para {perfil_id}")
