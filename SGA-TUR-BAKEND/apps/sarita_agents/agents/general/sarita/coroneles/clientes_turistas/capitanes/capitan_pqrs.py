from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanPqrs(CapitanTemplate):
    """
    Misión: Gestionar el ciclo de vida completo de las Peticiones, Quejas,
    Reclamos y Sugerencias (PQRS) de los turistas, asegurando una respuesta
    oportuna, una resolución efectiva y un registro para la mejora continua.
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
            nombre=f"Plan de Gestión de PQRS",
            descripcion=f"Gestionar PQRS para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="pqrs",
            descripcion="Procesar y gestionar una PQRS.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
