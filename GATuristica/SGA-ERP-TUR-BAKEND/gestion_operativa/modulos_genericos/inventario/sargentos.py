import logging
from .models import InventoryItem
logger = logging.getLogger(__name__)
class SargentoInventario:
    @staticmethod
    def descontar_stock(item_id, cantidad):
        from .services import InventarioService
        return InventarioService.update_stock(item_id, -cantidad)
