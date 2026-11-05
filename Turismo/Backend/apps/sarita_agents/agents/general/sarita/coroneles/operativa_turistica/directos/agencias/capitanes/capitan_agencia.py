from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico
from apps.sarita_agents.agents.general.sarita.coroneles.operativa_turistica.directos.tenientes_especializados import TenienteOperativoAgencia

class CapitanAgencia(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"teniente_agencia": TenienteOperativoAgencia()}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "teniente_agencia",
                "descripcion": f"Operación de Agencia: {mision.directiva_original.get('action')}",
                "parametros": mision.directiva_original.get('parameters', {})
            }
        }
        p.save()
        return p
