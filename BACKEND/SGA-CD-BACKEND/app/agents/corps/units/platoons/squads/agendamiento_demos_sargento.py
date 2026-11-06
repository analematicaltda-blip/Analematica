from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_agendar_demo_deportiva, tool_agendar_demo_cultural, tool_verificar_cupo_escenario, tool_enviar_pase_qr, tool_recordatorio_demo_24h

def get_agendamiento_demos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_agendar_demo_deportiva, tool_agendar_demo_cultural, tool_verificar_cupo_escenario, tool_enviar_pase_qr, tool_recordatorio_demo_24h]
        builder = SargentoGraphBuilder(squad, squad_name="AgendamientoDemosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AgendamientoDemosSargento listo para el despliegue.")
    return build_sargento_agent
