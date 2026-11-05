from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanTurismoLocal(CapitanTemplate):
    """
    Misión: Fomentar y gestionar el turismo a nivel municipal,
    promocionando los atractivos locales, coordinando con los prestadores
    de servicios del municipio y desarrollando el inventario turístico.
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
            nombre=f"Plan de Turismo Local",
            descripcion=f"Fomentar el turismo local para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="turismo_local",
            descripcion="Ejecutar el plan de fomento del turismo a nivel municipal.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
