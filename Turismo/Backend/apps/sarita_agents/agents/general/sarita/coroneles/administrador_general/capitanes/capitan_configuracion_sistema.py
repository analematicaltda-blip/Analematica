from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanConfiguracionSistema(CapitanTemplate):
    """
    Misión: Gestionar y aplicar configuraciones globales del sistema, como
    parámetros de entorno, toggles de funcionalidades (feature flags), o
    ajustes de rendimiento, asegurando consistencia y control.
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
            nombre=f"Plan de Configuración del Sistema",
            descripcion=f"Aplicar configuración para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="configuracion_sistema",
            descripcion="Aplicar los cambios de configuración en el sistema.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
