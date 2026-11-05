from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanBusquedaDocumental(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"busqueda": "admin_persistencia_archivistica", "acceso": "archivistico_acceso"}

    def plan(self, mision):
        pasos = {"1": {"teniente": "busqueda", "descripcion": "Buscar documentos por criterios.", "parametros": mision.directiva_original.get("parameters", {})}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
