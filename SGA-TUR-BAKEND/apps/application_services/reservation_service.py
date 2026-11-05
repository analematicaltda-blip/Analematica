import logging
from typing import Dict, Any
from .domain_contracts.base import (
    IApplicationService, DomainCommand, CreateReservationCommand, ConfirmReservationCommand
)

logger = logging.getLogger(__name__)

class ReservationApplicationService(IApplicationService):
    """
    Application Service for Reservations.
    Acts as an entry point for agents to interact with the reservation domain
    without knowing the underlying implementation or models.
    """

    def execute(self, command: DomainCommand) -> Dict[str, Any]:
        logger.info(f"Executing command {type(command).__name__}: {command.correlation_id}")

        try:
            if isinstance(command, CreateReservationCommand):
                from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.sargentos import SargentoReservas
                sargento = SargentoReservas()
                result = sargento.crear_reserva_automatica(
                    perfil_id=command.provider_id,
                    cliente_id=command.customer_id,
                    monto=command.total_amount
                )
                return {
                    "success": True,
                    "reservation_id": str(result.id) if hasattr(result, 'id') else "SIM-123"
                }

            elif isinstance(command, ConfirmReservationCommand):
                from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.sargentos import SargentoReservas
                SargentoReservas.confirmar_reserva(command.reserva_id)
                return {"success": True, "reserva_id": command.reserva_id}

            return {"success": False, "error": "Comando no soportado"}

        except Exception as e:
            logger.error(f"Error in ReservationApplicationService: {str(e)}")
            return {"success": False, "error": str(e)}
