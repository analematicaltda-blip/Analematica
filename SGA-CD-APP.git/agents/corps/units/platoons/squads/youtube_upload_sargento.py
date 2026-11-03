from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_yt_validar_oauth, tool_yt_resumable_upload, tool_yt_categoria_tags, tool_yt_asignar_playlist, tool_yt_verificar_estado

def get_youtube_upload_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_yt_validar_oauth, tool_yt_resumable_upload, tool_yt_categoria_tags, tool_yt_asignar_playlist, tool_yt_verificar_estado]
        builder = SargentoGraphBuilder(squad, squad_name="YoutubeUploadSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento YoutubeUploadSargento listo para el despliegue.")
    return build_sargento_agent
