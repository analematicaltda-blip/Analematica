from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from apps.sarita_agents.models import TareaDelegada
from ..sargentos.sargento_turista import SargentoAtencionTurista
from ..soldados.soldados_turistas import SoldadoBuscadorServicios

class TenientebusquedaServicios(TenienteTemplate):
    """
    Teniente encargado de la búsqueda inteligente de servicios para el turista.
    """
    def execute_task(self, tarea: TareaDelegada):
        self.logger.info(f"TENIENTE {self.__class__.__name__}: Iniciando búsqueda de servicios.")

        # 1. Coordinación vía Sargento
        sargento = SargentoAtencionTurista(teniente=self)
        sargento_report = sargento.handle_mission(tarea.parametros_especificos)

        # 2. Ejecución de búsqueda vía Soldado
        soldado = SoldadoBuscadorServicios()
        search_result = soldado.perform_action(tarea.parametros_especificos)

        resultado = {
            "status": "SUCCESS",
            "sargento_report": sargento_report,
            "search_result": search_result
        }

        self.mark_task_as_success(tarea, str(resultado))
