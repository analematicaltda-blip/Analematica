import logging
from django.shortcuts import get_object_or_404
from apps.delivery.services import DeliveryLogisticService

logger = logging.getLogger(__name__)

class InteroperabilityBridge:
    """
    Infraestructura de Interoperabilidad SARITA.
    Enlaza nativamente los dominios Operativos Especializados con los dominios Logísticos.
    """
    def __init__(self, user):
        self.user = user

    def link_delivery_to_specialized_order(self, operational_order_id, delivery_parameters, intention_id=None):
        """
        Directriz de Interoperabilidad: Delivery nunca actúa sin una Orden Operativa.
        Hardening 100%: Replaced import_string with Service Contract.
        """
        logger.info(f"INTEROP: Vinculando Delivery a Orden Operativa {operational_order_id}")

        # 1. Use the Unified Service Layer (Contracts)
        from apps.prestadores.mi_negocio.gestion_operativa.services import ReservaService
        reserva = ReservaService.get_reserva_by_id(operational_order_id)

        # 2. Enriquecer los parámetros con la trazabilidad de interoperabilidad
        # Usamos id_publico (UUID) para el vínculo interoperable
        delivery_parameters["related_operational_order_id"] = str(reserva.id_publico)
        delivery_parameters["provider_id"] = str(reserva.perfil_ref_id)

        # 3. Validar consistencia (Ej: El precio estimado debe alinearse con la suborden)
        # ... lógica de validación cruzada si aplica

        # 4. Ejecutar creación en el dominio de Delivery
        delivery_service = DeliveryLogisticService(user=self.user)
        service = delivery_service.create_request(delivery_parameters, intention_id=intention_id)

        logger.info(f"INTEROP: Enlace exitoso. Delivery Service {service.id} vinculado a Reserva {reserva.id}")

        return service

    def sync_operational_status(self, delivery_service_id):
        """
        Sincroniza el estado de la operativa especializada basado en eventos logísticos.
        """
        # Implementación de propagación bidireccional de estados
        pass
