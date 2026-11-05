from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanNominaBase(CapitanTemplate):
    """
    Clase base para los capitanes del módulo de Nómina.
    """

    def plan(self, mision):
        """
        El corazón del Capitán. Aquí es donde defines el plan táctico.
        """
        # Implementación por defecto: crear plan vacío
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {}
        plan.save()
        return plan

    def _get_tenientes(self) -> dict:
        return {}
