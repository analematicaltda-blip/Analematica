from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanFidelizacionLealtad(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"points_manager": "points_manager", "reward_fulfillment": "reward_fulfillment"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "points_manager", "descripcion": "Asignar puntos", "parametros": {}}}
        p.save()
        return p
