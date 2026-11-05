from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_canvas_post_1080x1080, tool_titular_jerarquia_post, tool_aislar_sujeto_png, tool_degradado_institucional, tool_insertar_logos_entidad

def get_post_cuadrado_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_canvas_post_1080x1080, tool_titular_jerarquia_post, tool_aislar_sujeto_png, tool_degradado_institucional, tool_insertar_logos_entidad]
        builder = SargentoGraphBuilder(squad, squad_name="PostCuadradoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PostCuadradoSargento listo para el despliegue.")
    return build_sargento_agent
