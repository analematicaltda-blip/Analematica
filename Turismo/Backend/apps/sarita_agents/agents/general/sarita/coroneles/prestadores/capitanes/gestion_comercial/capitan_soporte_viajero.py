from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanSoporteViajero(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"ticket_handler": "ticket_handler", "emergency_response": "emergency_response"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "ticket_handler", "descripcion": "Gestionar soporte", "parametros": {}}}
        p.save()
        return p
