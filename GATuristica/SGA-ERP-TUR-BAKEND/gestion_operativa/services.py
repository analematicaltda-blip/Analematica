# backend/apps/prestadores/mi_negocio/gestion_operativa/services.py
from .modulos_genericos.clientes.models import Cliente
from .modulos_genericos.perfil.models import ProviderProfile
from .modulos_genericos.productos_servicios.models import Product
from .modulos_genericos.reservas.models import Reserva

class ClienteService:
    @staticmethod
    def get_cliente_by_id(cliente_id):
        """
        Recupera un cliente por su ID público (UUID).
        """
        try:
            return Cliente.objects.get(id_publico=cliente_id)
        except Cliente.DoesNotExist:
            return None

class ProviderProfileService:
    @staticmethod
    def get_profile_by_id(profile_id):
        """
        Recupera un perfil de prestador por su ID (UUID).
        """
        try:
            # El ID principal de ProviderProfile ya es un UUID.
            return ProviderProfile.objects.get(id=profile_id)
        except ProviderProfile.DoesNotExist:
            return None

class ProductoService:
    @staticmethod
    def get_product_by_id(product_id):
        """
        Recupera un producto/servicio por su ID público (UUID).
        """
        try:
            return Product.objects.get(id_publico=product_id)
        except Product.DoesNotExist:
            return None

class ReservaService:
    @staticmethod
    def get_reserva_by_id(reserva_id):
        """
        Recupera una reserva por su ID público (UUID).
        """
        try:
            return Reserva.objects.get(id_publico=reserva_id)
        except Reserva.DoesNotExist:
            return None
