from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanPrevencionFraude(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"anomaly_detector": "anomaly_detector", "risk_scorer": "risk_scorer"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "anomaly_detector", "descripcion": "Detectar fraude", "parametros": {}}}
        p.save()
        return p
