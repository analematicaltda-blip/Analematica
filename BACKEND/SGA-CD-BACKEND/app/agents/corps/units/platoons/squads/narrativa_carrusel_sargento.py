from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_definir_slides_carrusel, tool_slide_portada_hook, tool_slides_cuerpo_educativo, tool_slide_cierre_cta, tool_continuidad_visual_flechas

def get_narrativa_carrusel_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_definir_slides_carrusel, tool_slide_portada_hook, tool_slides_cuerpo_educativo, tool_slide_cierre_cta, tool_continuidad_visual_flechas]
        builder = SargentoGraphBuilder(squad, squad_name="NarrativaCarruselSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento NarrativaCarruselSargento listo para el despliegue.")
    return build_sargento_agent
