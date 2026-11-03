from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_metricas_likes, tool_metricas_comentarios, tool_metricas_nuevos_seguidores, tool_metricas_engagement_rate, tool_metricas_clics_bio

def get_metricas_engagement_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_metricas_likes, tool_metricas_comentarios, tool_metricas_nuevos_seguidores, tool_metricas_engagement_rate, tool_metricas_clics_bio]
        builder = SargentoGraphBuilder(squad, squad_name="MetricasEngagementSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento MetricasEngagementSargento listo para el despliegue.")
    return build_sargento_agent
