from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanImpuestos(CapitanTemplate):
    """
    Misión: Garantizar el cumplimiento de todas las obligaciones fiscales, calculando y declarando impuestos de manera precisa y oportuna para evitar sanciones.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        from ...tenientes.teniente_impuestos import TenienteImpuestos
        return {
            "gestion_impuestos": TenienteImpuestos()
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "gestion_impuestos",
                "descripcion": "Cálculo y registro de obligaciones tributarias.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p

