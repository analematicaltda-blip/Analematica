from apps.sarita_agents.agents.capitan_template import CapitanTemplate

from apps.sarita_agents.tasks import TenienteGenericoComercial

class CapitanMarketing(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"seo_technical": TenienteGenericoComercial()}

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "seo_technical", "descripcion": "Ejecución comercial", "parametros": {}}}
        p.save()
        return p
