import logging
logger = logging.getLogger(__name__)
class ProductoService:
    @staticmethod
    def get_active_products(perfil_id):
        from .models import Product
        return Product.objects.filter(provider_id=perfil_id, is_active=True)
