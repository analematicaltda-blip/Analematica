import logging
logger = logging.getLogger(__name__)
class SargentoProductos:
    @staticmethod
    def validar_oferta(producto_id):
        logger.info(f"SARGENTO: Validando oferta de producto {producto_id}")
        return True
