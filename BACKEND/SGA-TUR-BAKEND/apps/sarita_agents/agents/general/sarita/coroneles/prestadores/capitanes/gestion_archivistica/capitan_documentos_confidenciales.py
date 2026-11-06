from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanDocumentosConfidenciales(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"archivado": "admin_persistencia_archivistica"}

    def plan(self, mision):
        pasos = {"1": {"teniente": "archivado", "descripcion": "Archivar documento confidencial con cifrado.", "parametros": mision.directiva_original.get("parameters", {})}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
