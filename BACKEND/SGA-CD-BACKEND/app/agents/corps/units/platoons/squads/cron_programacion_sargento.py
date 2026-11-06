from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_calcular_mejor_hora, tool_insertar_cronograma, tool_monitorear_disparo_cola, tool_reintentar_fallo_backoff, tool_cancelar_programacion

def get_cron_programacion_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_calcular_mejor_hora, tool_insertar_cronograma, tool_monitorear_disparo_cola, tool_reintentar_fallo_backoff, tool_cancelar_programacion]
        builder = SargentoGraphBuilder(squad, squad_name="CronProgramacionSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento CronProgramacionSargento listo para el despliegue.")
    return build_sargento_agent
