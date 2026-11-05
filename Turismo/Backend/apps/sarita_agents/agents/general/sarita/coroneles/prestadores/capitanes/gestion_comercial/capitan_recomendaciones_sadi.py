from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanRecomendacionesSADI(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"matching_engine": "matching_engine", "personalization": "personalization"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "matching_engine", "descripcion": "Matching oferta-demanda", "parametros": {}}}
        p.save()
        return p
