from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_pipeline_valor_estimado, tool_pipeline_fecha_cierre, tool_pipeline_dias_estancamiento, tool_pipeline_alerta_riesgo, tool_pipeline_bitacora_cambios

def get_control_tiempos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_pipeline_valor_estimado, tool_pipeline_fecha_cierre, tool_pipeline_dias_estancamiento, tool_pipeline_alerta_riesgo, tool_pipeline_bitacora_cambios]
        builder = SargentoGraphBuilder(squad, squad_name="ControlTiemposSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ControlTiemposSargento listo para el despliegue.")
    return build_sargento_agent
