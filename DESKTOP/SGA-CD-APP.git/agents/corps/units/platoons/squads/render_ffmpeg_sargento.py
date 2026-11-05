from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_render_reel_1080x1920, tool_render_video_1920x1080, tool_colorimetria_institucional, tool_optimizar_bitrate_h264, tool_extraer_thumbnail_poster

def get_render_ffmpeg_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_render_reel_1080x1920, tool_render_video_1920x1080, tool_colorimetria_institucional, tool_optimizar_bitrate_h264, tool_extraer_thumbnail_poster]
        builder = SargentoGraphBuilder(squad, squad_name="RenderFfmpegSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento RenderFfmpegSargento listo para el despliegue.")
    return build_sargento_agent
