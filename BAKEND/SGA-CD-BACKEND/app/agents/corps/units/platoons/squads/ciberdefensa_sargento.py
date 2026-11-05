from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_ciberseguridad_completo import (
    tool_detectar_anomalia_ddos,
    tool_mitigar_ataque_ddos,
    tool_aislar_ip_maliciosa_waf
)

def get_ciberdefensa_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_detectar_anomalia_ddos,
            tool_mitigar_ataque_ddos,
            tool_aislar_ip_maliciosa_waf
        ]
        builder = SargentoGraphBuilder(squad, squad_name="CiberdefensaSargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
