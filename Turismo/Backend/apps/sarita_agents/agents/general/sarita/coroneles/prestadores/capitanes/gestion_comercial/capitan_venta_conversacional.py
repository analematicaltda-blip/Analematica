from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanVentaConversacional(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"nlp_handler": "nlp_handler", "sales_closure": "sales_closure"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "nlp_handler", "descripcion": "Interacción natural", "parametros": {}}}
        p.save()
        return p
