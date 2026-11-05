import logging
from .models import Cliente
logger = logging.getLogger(__name__)
class SargentoClientes:
    @staticmethod
    def crear_cliente(perfil_id, data):
        from .services import ClienteService
        return ClienteService.create_cliente(perfil_id, data)
