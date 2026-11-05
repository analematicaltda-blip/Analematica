import logging
from .models import Costo
logger = logging.getLogger(__name__)
class SargentoCostos:
    @staticmethod
    def registrar_gasto(perfil_id, data):
        from .services import CostoService
        return CostoService.registrar_costo(perfil_id, data)
