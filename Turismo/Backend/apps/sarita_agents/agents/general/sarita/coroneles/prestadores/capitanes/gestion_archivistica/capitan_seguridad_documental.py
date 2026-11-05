from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanSeguridadDocumental(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"acceso": "archivistico_acceso", "integridad": "archivistico_integridad"}

    def plan(self, mision):
        pasos = {"1": {"teniente": "integridad", "descripcion": "Verificar seguridad y cifrado.", "parametros": mision.directiva_original.get("parameters", {})}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
