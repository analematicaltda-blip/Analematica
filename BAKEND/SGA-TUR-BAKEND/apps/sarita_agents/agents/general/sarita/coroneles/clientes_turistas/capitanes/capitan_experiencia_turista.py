from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanExperienciaTurista(CapitanTemplate):
    """
    Misión: Mejorar la experiencia del turista durante su viaje, gestionando
    puntos de contacto, resolviendo problemas en tiempo real, y recogiendo
    feedback para asegurar una estancia memorable.
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
            nombre=f"Plan de Experiencia del Turista",
            descripcion=f"Mejorar la experiencia para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="experiencia_turista",
            descripcion="Gestionar y mejorar la experiencia del turista.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
