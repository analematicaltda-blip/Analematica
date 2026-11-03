from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_detectar_inasistencias_3, tool_alerta_factura_por_vencer, tool_tarea_llamada_retencion, tool_pausa_temporal_matricula, tool_encuesta_salida_retiro

def get_prevencion_desercion_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_detectar_inasistencias_3, tool_alerta_factura_por_vencer, tool_tarea_llamada_retencion, tool_pausa_temporal_matricula, tool_encuesta_salida_retiro]
        builder = SargentoGraphBuilder(squad, squad_name="PrevencionDesercionSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PrevencionDesercionSargento listo para el despliegue.")
    return build_sargento_agent
