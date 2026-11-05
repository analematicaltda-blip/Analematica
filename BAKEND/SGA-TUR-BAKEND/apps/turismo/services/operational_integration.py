import logging
from django.db import transaction
from .financial_service import TourismFinancialService
from .delivery_integration import TourismDeliveryService
from apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.gastronomia.models import Plato, Restaurante
from ..models.provider_models import TourismProvider, Reservation

logger = logging.getLogger(__name__)

class OperationalIntegrationService:
    """
    Orquesta la integración entre operaciones especializadas, finanzas y logística.
    """

    @staticmethod
    @transaction.atomic
    def process_restaurant_sale(plato_id, customer, delivery_required=False, address=None):
        """
        Procesa una venta de gastronomía: Registro -> Pago -> Delivery.
        """
        plato = Plato.objects.get(id=plato_id)
        restaurante = plato.categoria.menu.restaurante
        provider = TourismProvider.objects.filter(owner=restaurante.perfil.usuario).first()

        # 1. Pago via Wallet
        tx = TourismFinancialService.register_transaction(
            provider=provider,
            amount=plato.producto.precio_venta,
            customer=customer,
            description=f"Consumo: {plato.producto.nombre}"
        )

        # 2. Generar Delivery si es requerido
        delivery_request = None
        if delivery_required and restaurante.ofrece_delivery:
            delivery_request = TourismDeliveryService.create_delivery(
                provider=provider,
                customer=customer,
                items=[{"description": plato.producto.nombre, "quantity": 1}],
                address=address
            )

        return {
            "status": "SUCCESS",
            "transaction_id": str(tx.id),
            "delivery_id": str(delivery_request.id) if delivery_request else None,
            "delivery_status": "CREATED" if delivery_request else "N/A"
        }
