from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanControlPrestadores(CapitanTemplate):
    """
    Misión: Supervisar y controlar a los prestadores de servicios turísticos
    del municipio, asegurando el cumplimiento de la normativa, la calidad
    del servicio y la formalización (RNT).
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
            nombre=f"Plan de Control de Prestadores",
            descripcion=f"Supervisar prestadores para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="control_prestadores",
            descripcion="Ejecutar la supervisión y control de los prestadores de servicios.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
