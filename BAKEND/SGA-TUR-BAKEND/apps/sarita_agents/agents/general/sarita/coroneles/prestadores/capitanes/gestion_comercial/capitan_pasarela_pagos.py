from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanPasarelaPagos(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"payment_gateway": "payment_gateway", "reconciliation": "reconciliation"}
    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "payment_gateway", "descripcion": "Procesar pago", "parametros": {}}}
        p.save()
        return p
