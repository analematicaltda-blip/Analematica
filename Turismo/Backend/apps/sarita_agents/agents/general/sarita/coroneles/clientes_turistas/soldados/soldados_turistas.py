# backend/apps/sarita_agents/agents/general/sarita/coroneles/clientes_turistas/soldados/soldados_turistas.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoBuscadorServicios(SoldadoN6OroV2):
    domain = "clientes_turistas"
    aggregate_root = "Product"
    required_permissions = ["clientes_turistas.execute"]

    """Busca servicios disponibles basados en preferencias del turista."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO TURISTA: Buscando -> {params.get('query')}")
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
        query = params.get('query', '')
        results = Product.objects.filter(nombre__icontains=query)
        return {"status": "RESULTS_FOUND", "count": results.count()}

class SoldadoGestorReservas(SoldadoN6OroV2):
    domain = "clientes_turistas"
    aggregate_root = "Reservation"
    required_permissions = ["clientes_turistas.execute"]

    """Ejecuta y confirma reservas para el turista."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO TURISTA: Reservando -> {params.get('servicio_id')}")
        from apps.domain_business.operativa.models import Reservation
        from django.utils import timezone

        reserva = Reservation.objects.create(
            tenant_id=params.get('tenant_id'),
            customer_id=params.get('customer_id'),
            content_type_id=params.get('content_type_id'),
            object_id=params.get('servicio_id'),
            start_date=params.get('start_date', timezone.now()),
            end_date=params.get('end_date', timezone.now() + timezone.timedelta(days=1)),
            total_price=params.get('price', 0.0),
            status=Reservation.Status.PENDING
        )
        return reserva

class SoldadoSoportePQRS(SoldadoN6OroV2):
    domain = "clientes_turistas"
    aggregate_root = "PQRS"
    required_permissions = ["clientes_turistas.execute"]

    """Atiende y clasifica quejas o reclamos del turista."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO TURISTA: Procesando PQRS -> {params.get('asunto')}")
        # Lógica de registro de soporte
        return {"status": "FILED", "radicado": "RAD-2024-001", "asunto": params.get('asunto')}
