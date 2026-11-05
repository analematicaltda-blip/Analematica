from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanInventarios(CapitanTemplate):
    """
    Misión: Supervisar y registrar los movimientos de inventario, asegurando la correcta valoración de existencias y el control de mermas.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        from ...tenientes.teniente_inventario import TenienteInventario
        return {
            "control_inventario": TenienteInventario()
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)

        p.pasos_del_plan = {
            "1": {
                "teniente": "control_inventario",
                "descripcion": "Gestión de movimientos y control de stock.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p

