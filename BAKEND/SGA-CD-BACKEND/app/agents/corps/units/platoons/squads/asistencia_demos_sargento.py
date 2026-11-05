from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_confirmar_asistencia_demo, tool_registrar_asistio_demo, tool_reagendar_demo, tool_solicitar_feedback_demo, tool_oferta_cierre_inmediato

def get_asistencia_demos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_confirmar_asistencia_demo, tool_registrar_asistio_demo, tool_reagendar_demo, tool_solicitar_feedback_demo, tool_oferta_cierre_inmediato]
        builder = SargentoGraphBuilder(squad, squad_name="AsistenciaDemosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AsistenciaDemosSargento listo para el despliegue.")
    return build_sargento_agent
