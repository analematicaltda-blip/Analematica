from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_generar_srt_sincronizado, tool_quemar_subtitulos_video, tool_resaltar_keywords_color, tool_sincronizar_timing_subtitulos, tool_zona_segura_subtitulos

def get_subtitulos_dinamicos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_generar_srt_sincronizado, tool_quemar_subtitulos_video, tool_resaltar_keywords_color, tool_sincronizar_timing_subtitulos, tool_zona_segura_subtitulos]
        builder = SargentoGraphBuilder(squad, squad_name="SubtitulosDinamicosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento SubtitulosDinamicosSargento listo para el despliegue.")
    return build_sargento_agent
