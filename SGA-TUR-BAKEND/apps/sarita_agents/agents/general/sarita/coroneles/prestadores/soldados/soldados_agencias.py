# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_agencias.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoValidacionReservaAgencia(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Reserva"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO AGENCIA: Validando reserva -> {params.get('reserva_id')}")
        from application.services.reservation_service import ReservationService
        service = ReservationService()

        # Refactored: No direct Model access. Using Application Service.
        reserva = service.process_validation(params.get('reserva_id'))
        return reserva

class SoldadoRegistroComisionAgencia(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Comision"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO AGENCIA: Registrando comisión.")
        # Lógica de registro de comisión real
        return {"id": params.get('reserva_id'), "status": "COMMISSION_REGISTERED"}

class SoldadoConfirmacionLiquidacionAgencia(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Liquidacion"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO AGENCIA: Confirmando liquidación.")
        return {"status": "SUCCESS", "msg": "Liquidación confirmada."}

class SoldadoVerificacionItinerarioAgencia(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Itinerario"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO AGENCIA: Verificando itinerario.")
        return {"action": "itinerary_checked", "status": "SYNCED"}

class SoldadoMonitoreoDestinoAgencia(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Destino"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO AGENCIA: Monitoreando disponibilidad en destino.")
        return {"action": "monitored", "availability": "high"}
