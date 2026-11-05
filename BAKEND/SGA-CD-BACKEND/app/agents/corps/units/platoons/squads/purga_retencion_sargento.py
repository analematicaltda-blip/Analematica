from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_limpiar_temporales_render, tool_purgar_archivos_antiguos, tool_calcular_espacio_disco, tool_alerta_umbral_storage_90, tool_comprimir_historicos_tar

def get_purga_retencion_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_limpiar_temporales_render, tool_purgar_archivos_antiguos, tool_calcular_espacio_disco, tool_alerta_umbral_storage_90, tool_comprimir_historicos_tar]
        builder = SargentoGraphBuilder(squad, squad_name="PurgaRetencionSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PurgaRetencionSargento listo para el despliegue.")
    return build_sargento_agent
