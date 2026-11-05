from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanCoordinacionMunicipal(CapitanTemplate):
    """
    Misión: Servir como enlace entre el nivel departamental y los municipios,
    facilitando la comunicación, recogiendo datos, y asegurando que las
    políticas y planes regionales se implementen de forma coordinada.
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
            nombre=f"Plan de Coordinación Municipal",
            descripcion=f"Coordinar con municipios para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="coordinacion_municipal",
            descripcion="Ejecutar la coordinación con los diferentes municipios.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
