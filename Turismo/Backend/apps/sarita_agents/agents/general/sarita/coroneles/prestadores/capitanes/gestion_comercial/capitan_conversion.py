from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

from apps.sarita_agents.tasks import TenienteActivacionOperativa

class CapitanConversion(CapitanTemplate):
    """
    Capitán de Conversión: Encargado de cerrar la venta y activar la operación.
    """
    def _get_tenientes(self) -> dict:
        return {"comercial_activacion": TenienteActivacionOperativa()}

    def plan(self, mision):
        pasos = {
            "1": {
                "teniente": "comercial_activacion",
                "descripcion": "Activar orden operativa a partir del contrato.",
                "parametros": {"contrato_id": mision.directiva_original.get("parameters", {}).get("contrato_id")}
            }
        }
        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )
