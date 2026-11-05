from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanRutasTuristicas(CapitanTemplate):
    """
    Misión: Diseñar, desarrollar y promocionar rutas turísticas a nivel
    departamental, integrando atractivos, servicios y experiencias de
    múltiples municipios para crear productos turísticos competitivos.
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
            nombre=f"Plan de Rutas Turísticas",
            descripcion=f"Desarrollar rutas turísticas para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="rutas_turisticas",
            descripcion="Diseñar y promocionar las rutas turísticas del departamento.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
