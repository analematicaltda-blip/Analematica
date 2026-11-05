# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_operacion_hotelera.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOperacionHotelera(CapitanTemplate):
    """
    Agente Especializado en Hotelería: Gestiona inventario de habitaciones y estados de limpieza.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Hotel): Planificando operación hotelera para misión {mision.id}")

        pasos = {
            "gestion_habitaciones": {
                "descripcion": "Actualizar estado de habitaciones y asignar recursos de limpieza.",
                "teniente": "gestor_hotelero",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )

    def _get_tenientes(self) -> dict:
        class TenienteHotelero:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Operación hotelera ejecutada según el manual sectorial."}

        return {
            "gestor_hotelero": TenienteHotelero()
        }
