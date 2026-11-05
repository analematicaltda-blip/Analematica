from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanPlanificacionFinanciera(CapitanTemplate):
    """
    Misión: Desarrollar modelos y proyecciones financieras a largo plazo para
    apoyar la toma de decisiones estratégicas, como inversiones o expansión.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        return {}
    def plan(self):
        """
        El corazón del Capitán. Aquí es donde defines el plan táctico.
        Debes crear un PlanTáctico y luego delegar Tareas a los Tenientes.
        """

        # 1. Crear el Plan Táctico
        plan_tactico = self.get_or_create_plan_tactico(
            nombre="Plan de Ejecución para CapitanPlanificacionFinanciera",
            descripcion=f"Este plan detalla los pasos para cumplir el objetivo: {self.objective}"
        )

        # 2. Definir y Delegar Tareas (EJEMPLO - DEBE SER IMPLEMENTADO)
        # self.delegar_tarea(plan_tactico=plan_tactico, nombre_teniente="...", descripcion="...", parametros_especificos={...})

        # 3. Lanzar la Ejecución del Plan
        self.lanzar_ejecucion_plan()

