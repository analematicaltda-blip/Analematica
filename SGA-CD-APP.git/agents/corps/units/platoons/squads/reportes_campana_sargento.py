from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_informe_kpis_semanal, tool_informe_comparar_redes, tool_informe_costo_por_lead, tool_informe_top_publicacion, tool_informe_resumen_pdf

def get_reportes_campana_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_informe_kpis_semanal, tool_informe_comparar_redes, tool_informe_costo_por_lead, tool_informe_top_publicacion, tool_informe_resumen_pdf]
        builder = SargentoGraphBuilder(squad, squad_name="ReportesCampanaSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ReportesCampanaSargento listo para el despliegue.")
    return build_sargento_agent
