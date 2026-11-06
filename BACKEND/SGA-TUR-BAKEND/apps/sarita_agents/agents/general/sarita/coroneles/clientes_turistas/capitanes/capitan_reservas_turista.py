from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanReservasTurista(CapitanTemplate):
    """
    Misión: Gestionar el ciclo de vida de las reservas de un turista,
    desde la creación y confirmación hasta la modificación o cancelación,
    asegurando la comunicación con los prestadores de servicios.
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
            nombre=f"Plan de Gestión de Reservas",
            descripcion=f"Gestionar reserva para el objetivo: {self.objective}"
        )

        self.delegar_tarea(
            plan_tactico=plan_tactico,
            nombre_teniente="reservas_turista",
            descripcion="Realizar operaciones sobre la reserva de un turista.",
            parametros_especificos=self.parametros
        )

        self.lanzar_ejecucion_plan()
