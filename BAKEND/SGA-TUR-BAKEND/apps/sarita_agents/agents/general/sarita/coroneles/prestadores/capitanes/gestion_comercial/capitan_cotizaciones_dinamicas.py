from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanCotizacionesDinamicas(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"pricing_engine": "pricing_engine"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "pricing_engine", "descripcion": "Calcular cotización", "parametros": {}}}
        p.save()
        return p
