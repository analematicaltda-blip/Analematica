from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_soporte_reproductor_android, tool_soporte_reproductor_ios, tool_pixel_format_yuv420p, tool_fragmentar_hls_m3u8, tool_validar_reproduccion_sin_cortes

def get_compatibilidad_so_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_soporte_reproductor_android, tool_soporte_reproductor_ios, tool_pixel_format_yuv420p, tool_fragmentar_hls_m3u8, tool_validar_reproduccion_sin_cortes]
        builder = SargentoGraphBuilder(squad, squad_name="CompatibilidadSoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento CompatibilidadSoSargento listo para el despliegue.")
    return build_sargento_agent
