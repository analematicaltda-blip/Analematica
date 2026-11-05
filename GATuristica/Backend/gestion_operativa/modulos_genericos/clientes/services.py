import logging
import uuid
from .models import Cliente

logger = logging.getLogger(__name__)

class ClienteService:
    @staticmethod
    def get_cliente_by_id(cliente_id):
        try:
            return Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return None

    @staticmethod
    def create_cliente(perfil, data):
        if 'id_publico' not in data:
            data['id_publico'] = uuid.uuid4()
        cliente = Cliente.objects.create(perfil=perfil, **data)
        logger.info(f"Cliente creado: {cliente.nombre} para perfil {perfil.id}")
        return cliente
