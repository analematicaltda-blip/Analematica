from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_tiktok_validar_token, tool_tiktok_upload_video, tool_tiktok_privacidad_duo, tool_tiktok_programar_hora, tool_tiktok_verificar_estado

def get_tiktok_pub_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_tiktok_validar_token, tool_tiktok_upload_video, tool_tiktok_privacidad_duo, tool_tiktok_programar_hora, tool_tiktok_verificar_estado]
        builder = SargentoGraphBuilder(squad, squad_name="TiktokPubSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento TiktokPubSargento listo para el despliegue.")
    return build_sargento_agent
