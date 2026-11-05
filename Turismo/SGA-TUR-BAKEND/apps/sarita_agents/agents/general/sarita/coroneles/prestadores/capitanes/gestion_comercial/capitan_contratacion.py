from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanContratacion(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"contratacion": "comercial_contratacion"}

    def plan(self, mision):
        pasos = {
            "1": {
                "teniente": "contratacion",
                "descripcion": "Generar contrato formal a partir de operación comercial.",
                "parametros": {"operacion_id": mision.directiva_original.get("parameters", {}).get("operacion_id")}
            }
        }
        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )
