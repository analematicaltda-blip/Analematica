from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanCostosInsumos(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"operativo_gestion_costos": "operativo_gestion_costos"}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "operativo_gestion_costos", "descripcion": "Ejecución de CapitanCostosInsumos", "parametros": mision.directiva_original.get('parameters', {})}}
        p.save()
        return p
