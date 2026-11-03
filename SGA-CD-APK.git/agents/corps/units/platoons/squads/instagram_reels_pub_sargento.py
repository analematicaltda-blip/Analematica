from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_ig_validar_graph_api, tool_ig_iniciar_contenedor, tool_ig_adjuntar_caption, tool_ig_publicar_reel, tool_ig_consultar_permalink

def get_instagram_reels_pub_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_ig_validar_graph_api, tool_ig_iniciar_contenedor, tool_ig_adjuntar_caption, tool_ig_publicar_reel, tool_ig_consultar_permalink]
        builder = SargentoGraphBuilder(squad, squad_name="InstagramReelsPubSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento InstagramReelsPubSargento listo para el despliegue.")
    return build_sargento_agent
