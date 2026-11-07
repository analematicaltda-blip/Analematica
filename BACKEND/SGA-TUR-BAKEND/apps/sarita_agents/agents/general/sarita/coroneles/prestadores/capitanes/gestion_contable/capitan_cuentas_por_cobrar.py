from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanCuentasPorCobrar(CapitanTemplate):
    """
    Misión: Gestionar y monitorear todas las cuentas por cobrar, optimizando el flujo de caja mediante el seguimiento proactivo de facturas y pagos pendientes.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        from ...tenientes.teniente_cartera import TenienteCartera
        return {
            "gestion_cartera": TenienteCartera()
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "gestion_cartera",
                "descripcion": "Recuperación y seguimiento de cuentas por cobrar.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p

