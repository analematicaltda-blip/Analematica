from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_titulos_alta_retencion, tool_copy_descripcion_post, tool_hashtags_estrategicos, tool_texto_portada_hook, tool_validar_limites_caracteres

def get_optimizacion_texto_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_titulos_alta_retencion, tool_copy_descripcion_post, tool_hashtags_estrategicos, tool_texto_portada_hook, tool_validar_limites_caracteres]
        builder = SargentoGraphBuilder(squad, squad_name="OptimizacionTextoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento OptimizacionTextoSargento listo para el despliegue.")
    return build_sargento_agent
