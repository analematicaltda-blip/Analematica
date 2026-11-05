from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

from apps.sarita_agents.agents.general.sarita.coroneles.operativa_turistica.directos.tenientes_especializados import TenienteOperativoTransporte

class CapitanMonitoreoRutas(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"teniente_transporte": TenienteOperativoTransporte()}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "teniente_transporte",
                "descripcion": "Actualizar progreso de ruta",
                "parametros": mision.directiva_original.get('parameters', {})
            }
        }
        p.save()
        return p
