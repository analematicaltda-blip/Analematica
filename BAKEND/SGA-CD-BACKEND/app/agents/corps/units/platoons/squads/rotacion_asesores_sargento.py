from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_asignar_round_robin, tool_asignar_especialidad, tool_asignar_geografia, tool_notificar_asesor, tool_reasignar_por_inactividad

def get_rotacion_asesores_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_asignar_round_robin, tool_asignar_especialidad, tool_asignar_geografia, tool_notificar_asesor, tool_reasignar_por_inactividad]
        builder = SargentoGraphBuilder(squad, squad_name="RotacionAsesoresSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento RotacionAsesoresSargento listo para el despliegue.")
    return build_sargento_agent
