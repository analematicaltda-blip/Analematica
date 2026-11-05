from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanKYCVerificacion(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"id_validator": "id_validator", "background_check": "background_check"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "id_validator", "descripcion": "Validar identidad", "parametros": {}}}
        p.save()
        return p
