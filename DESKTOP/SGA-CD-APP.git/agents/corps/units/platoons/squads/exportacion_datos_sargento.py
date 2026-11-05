from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_exportar_json_api, tool_actualizar_analitica_pg, tool_notificar_resumen_inquilino, tool_archivar_historico_campana, tool_limpiar_cache_metricas

def get_exportacion_datos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_exportar_json_api, tool_actualizar_analitica_pg, tool_notificar_resumen_inquilino, tool_archivar_historico_campana, tool_limpiar_cache_metricas]
        builder = SargentoGraphBuilder(squad, squad_name="ExportacionDatosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ExportacionDatosSargento listo para el despliegue.")
    return build_sargento_agent
