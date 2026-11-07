from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanLegalidadYPrivacidad(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"gdpr_compliance": "gdpr_compliance", "legal_terms": "legal_terms"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "gdpr_compliance", "descripcion": "Verificar privacidad", "parametros": {}}}
        p.save()
        return p
