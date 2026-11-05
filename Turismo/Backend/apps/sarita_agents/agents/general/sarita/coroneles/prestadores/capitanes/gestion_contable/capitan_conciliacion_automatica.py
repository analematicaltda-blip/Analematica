from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanConciliacionAutomatica(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"conciliacion": "admin_persistencia_contable"}

    def plan(self, mision):
        pasos = {"1": {"teniente": "conciliacion", "descripcion": "Ejecutar conciliacion automatica de saldos.", "parametros": mision.directiva_original.get("parameters", {})}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
