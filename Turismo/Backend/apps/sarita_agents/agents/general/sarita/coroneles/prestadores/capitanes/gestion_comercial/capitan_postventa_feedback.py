from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanPostventaFeedback(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"survey_manager": "survey_manager", "sentiment_analysis": "sentiment_analysis"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "survey_manager", "descripcion": "Recolectar feedback", "parametros": {}}}
        p.save()
        return p
