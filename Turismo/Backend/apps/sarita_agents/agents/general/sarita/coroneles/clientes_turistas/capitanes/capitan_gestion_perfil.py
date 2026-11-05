from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanGestionPerfil(CapitanTemplate):
    """
    Misión: Administrar el perfil del turista, incluyendo sus datos personales,
    preferencias de viaje, historial de reservas y configuración de
    notificaciones, garantizando la privacidad y personalización.
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
            nombre=f"Plan de Gestión de Perfil",
            descripcion=f"Gestionar perfil para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="gestion_perfil",
            descripcion="Realizar operaciones sobre el perfil del turista.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
