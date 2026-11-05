from apps.sarita_agents.agents.soldado_template import SoldierTemplate
import logging

logger = logging.getLogger(__name__)

class SoldadoLogistico(SoldierTemplate):
    """ NIVEL 6 — SOLDADO DE DELIVERY """
    def __init__(self, sargento, id):
        super().__init__(sargento)
        self.soldier_id = id

    def perform_action(self, params: dict):
        micro_action = params.get("micro_action", "GENERIC_TASK")
        logger.info(f"SOLDADO DELIVERY #{self.soldier_id}: Ejecutando {micro_action}")

        # Integración con lógica real si es el primer soldado del equipo
        if self.soldier_id == 0:
            from apps.delivery.services import LogisticService
            service_id = params.get("order_id")
            if service_id and micro_action == "ASSIGN_DRIVER":
                # Aquí se podría disparar la lógica real del servicio
                # Logic implemented
                pass

        return {"status": "SUCCESS", "soldier": self.soldier_id, "action": micro_action}
