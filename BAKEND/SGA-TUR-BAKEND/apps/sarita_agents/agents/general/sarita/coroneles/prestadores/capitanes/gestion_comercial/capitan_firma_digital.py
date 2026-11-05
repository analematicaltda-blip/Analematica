from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanFirmaDigital(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"signature_provider": "signature_provider", "evidence_vault": "evidence_vault"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "signature_provider", "descripcion": "Solicitar firma", "parametros": {}}}
        p.save()
        return p
