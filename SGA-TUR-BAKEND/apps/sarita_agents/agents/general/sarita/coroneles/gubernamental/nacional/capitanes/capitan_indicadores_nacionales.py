from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanIndicadoresNacionales(CapitanTemplate):
    """
    Misión: Recopilar, analizar y reportar los indicadores clave de turismo
    a nivel nacional (ocupación, gasto promedio, etc.), comparando el
    desempeño del departamento con las métricas nacionales.
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
            nombre=f"Plan de Indicadores Nacionales",
            descripcion=f"Analizar indicadores para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="indicadores_nacionales",
            descripcion="Recopilar y analizar los indicadores de turismo nacionales.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
