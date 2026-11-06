from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_redactar_guion_vertical, tool_crear_storyboard_escenas, tool_extraer_gancho_viral, tool_estructurar_cta_final, tool_calcular_tiempos_ritmo

def get_guion_storyboard_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_redactar_guion_vertical, tool_crear_storyboard_escenas, tool_extraer_gancho_viral, tool_estructurar_cta_final, tool_calcular_tiempos_ritmo]
        builder = SargentoGraphBuilder(squad, squad_name="GuionStoryboardSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento GuionStoryboardSargento listo para el despliegue.")
    return build_sargento_agent
