from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanAlianzasComerciales(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"partnership_manager": "partnership_manager"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "partnership_manager", "descripcion": "Gestionar convenios", "parametros": {}}}
        p.save()
        return p
