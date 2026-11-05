from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanCheckInCheckOut(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"teniente_hospedaje": "teniente_hospedaje"}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        m_type = mision.directiva_original.get("mission", {}).get("type")

        p.pasos_del_plan = {
            "1": {
                "teniente": "teniente_hospedaje",
                "descripcion": f"Procesar {m_type}",
                "parametros": mision.directiva_original.get('parameters', {})
            }
        }
        p.save()
        return p
