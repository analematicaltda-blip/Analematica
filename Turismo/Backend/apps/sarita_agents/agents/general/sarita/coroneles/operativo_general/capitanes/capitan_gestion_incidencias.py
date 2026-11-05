from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanGestionIncidencias(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"operativo_comercial": "operativo_comercial"}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "operativo_comercial", "descripcion": "Ejecución de CapitanGestionIncidencias", "parametros": mision.directiva_original.get('parameters', {})}}
        p.save()
        return p
