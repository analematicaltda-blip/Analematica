from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanPagosYTesoreria(CapitanTemplate):
    """
    Misión: Generación de archivos planos para bancos y control de la dispersión de pagos.
    """

    def plan(self, mision):
        """
        El corazón del Capitán. Aquí es donde defines el plan táctico.
        """
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {}
        plan.save()
        return plan

    def _get_tenientes(self) -> dict:
        return {}
