from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

class CapitanFacturacion(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        from ...tenientes.teniente_facturacion import TenienteFacturacion
        return {
            "gestion_facturacion": TenienteFacturacion()
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "gestion_facturacion",
                "descripcion": "Generación legal y validación de factura.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p
