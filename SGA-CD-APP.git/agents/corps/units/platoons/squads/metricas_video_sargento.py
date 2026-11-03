from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_metricas_vistas_reels, tool_metricas_tiempo_visualizacion, tool_metricas_tasa_retencion, tool_metricas_shares, tool_metricas_saves

def get_metricas_video_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_metricas_vistas_reels, tool_metricas_tiempo_visualizacion, tool_metricas_tasa_retencion, tool_metricas_shares, tool_metricas_saves]
        builder = SargentoGraphBuilder(squad, squad_name="MetricasVideoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento MetricasVideoSargento listo para el despliegue.")
    return build_sargento_agent
