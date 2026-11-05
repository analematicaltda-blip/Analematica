from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_crear_banner_1920x1080, tool_adaptar_hero_web, tool_integrar_datos_evento, tool_banner_email_header, tool_exportar_webp

def get_banner_horizontal_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_crear_banner_1920x1080, tool_adaptar_hero_web, tool_integrar_datos_evento, tool_banner_email_header, tool_exportar_webp]
        builder = SargentoGraphBuilder(squad, squad_name="BannerHorizontalSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento BannerHorizontalSargento listo para el despliegue.")
    return build_sargento_agent
