from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanFeedbackPostServicio(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"operativo_analisis_datos": "operativo_analisis_datos"}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "operativo_analisis_datos", "descripcion": "Ejecución de CapitanFeedbackPostServicio", "parametros": mision.directiva_original.get('parameters', {})}}
        p.save()
        return p
