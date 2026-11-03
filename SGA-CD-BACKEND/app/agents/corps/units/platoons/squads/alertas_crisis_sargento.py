from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_crisis_pico_negativo, tool_crisis_bloquear_campana, tool_crisis_reporte_incidente, tool_crisis_menciones_externas, tool_crisis_sugerir_respuesta

def get_alertas_crisis_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_crisis_pico_negativo, tool_crisis_bloquear_campana, tool_crisis_reporte_incidente, tool_crisis_menciones_externas, tool_crisis_sugerir_respuesta]
        builder = SargentoGraphBuilder(squad, squad_name="AlertasCrisisSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AlertasCrisisSargento listo para el despliegue.")
    return build_sargento_agent
