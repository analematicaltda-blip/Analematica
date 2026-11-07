from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from apps.sarita_agents.models import TareaDelegada

class TenienteturismoLocal(TenienteTemplate):
    """
    Teniente para capitan_turismo_local.
    Este es un teniente de placeholder con lógica simulada.
    """
    def execute_task(self, tarea: TareaDelegada):
        self.logger.info(f"TENIENTE {self.__class__.__name__}: Ejecutando tarea {{tarea.id}} para la misión {{tarea.plan_tactico.mision_id}}.")
        resultado = f"Tarea para {self.__class__.__name__} completada exitosamente."
        self.mark_task_as_success(tarea, resultado)
