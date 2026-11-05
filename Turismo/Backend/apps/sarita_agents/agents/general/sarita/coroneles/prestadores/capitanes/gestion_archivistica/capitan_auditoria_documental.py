from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanAuditoriaDocumental(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"auditoria": "archivistico_integridad"}

    def plan(self, mision):
        pasos = {"1": {"teniente": "auditoria", "descripcion": "Ejecutar auditoría de integridad sobre el expediente.", "parametros": mision.directiva_original.get("parameters", {})}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
