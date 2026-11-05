from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanPlanificacionRegional(CapitanTemplate):
    """
    Misión: Orquestar la planificación turística a nivel departamental,
    alineando las estrategias de los municipios y desarrollando planes
    regionales que potencien los atractivos del departamento.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        return {}
    def plan(self):
        """
        El corazón del Capitán. Aquí es donde defines el plan táctico.
        """

        plan_tactico = self.get_or_create_plan_tactico(
            nombre=f"Plan de Planificación Regional",
            descripcion=f"Desarrollar plan regional para el objetivo: {self.objective}"
        )

        # Esta es una aproximación. En una implementación real, podría delegar a varios tenientes.
        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="planificacion_regional", # Asumiendo que existirá un teniente con esta clave
            descripcion="Ejecutar la planificación turística a nivel departamental.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
