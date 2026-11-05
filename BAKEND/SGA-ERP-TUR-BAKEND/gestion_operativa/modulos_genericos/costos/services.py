import logging
from .models import Costo
logger = logging.getLogger(__name__)
class CostoService:
    @staticmethod
    def registrar_costo(perfil, data):
        costo = Costo.objects.create(perfil=perfil, **data)
        logger.info(f"Costo registrado: {costo.concepto} por ${costo.monto}")
        return costo
