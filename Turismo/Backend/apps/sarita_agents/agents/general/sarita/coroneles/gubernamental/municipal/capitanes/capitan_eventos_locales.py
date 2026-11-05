from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanEventosLocales(CapitanTemplate):
    """
    Misión: Gestionar la planificación, promoción y ejecución de eventos
    de interés turístico en el municipio (festivales, ferias, etc.),
    coordinando la logística y la participación de la comunidad.
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
            nombre=f"Plan de Eventos Locales",
            descripcion=f"Gestionar eventos para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="eventos_locales",
            descripcion="Ejecutar la planificación y promoción de eventos locales.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
