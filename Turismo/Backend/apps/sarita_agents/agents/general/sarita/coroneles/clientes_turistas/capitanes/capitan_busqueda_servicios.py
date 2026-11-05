from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanBusquedaServicios(CapitanTemplate):
    """
    Misión: Ayudar a los turistas a encontrar servicios (alojamiento,
    restaurantes, actividades) basados en sus preferencias, presupuesto,
    y disponibilidad, proporcionando recomendaciones personalizadas.
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
            nombre=f"Plan de Búsqueda de Servicios",
            descripcion=f"Buscar servicios para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="busqueda_servicios",
            descripcion="Realizar la búsqueda y recomendación de servicios.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
