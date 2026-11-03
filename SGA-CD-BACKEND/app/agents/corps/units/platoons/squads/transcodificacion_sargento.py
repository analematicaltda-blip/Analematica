from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_variante_video_720p, tool_variante_video_480p, tool_preview_gif_3seg, tool_extraer_audio_mp3, tool_ajustar_rotacion_metadata

def get_transcodificacion_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_variante_video_720p, tool_variante_video_480p, tool_preview_gif_3seg, tool_extraer_audio_mp3, tool_ajustar_rotacion_metadata]
        builder = SargentoGraphBuilder(squad, squad_name="TranscodificacionSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento TranscodificacionSargento listo para el despliegue.")
    return build_sargento_agent
