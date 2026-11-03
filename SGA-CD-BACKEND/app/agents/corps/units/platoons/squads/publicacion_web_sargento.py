from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_mover_a_assets_generated, tool_permisos_lectura_nginx, tool_enlace_publico_http, tool_codigo_qr_recurso, tool_headers_cache_control

def get_publicacion_web_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_mover_a_assets_generated, tool_permisos_lectura_nginx, tool_enlace_publico_http, tool_codigo_qr_recurso, tool_headers_cache_control]
        builder = SargentoGraphBuilder(squad, squad_name="PublicacionWebSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PublicacionWebSargento listo para el despliegue.")
    return build_sargento_agent
