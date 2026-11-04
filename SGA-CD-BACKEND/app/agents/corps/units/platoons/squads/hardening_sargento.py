from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_ciberseguridad_completo import (
    tool_escanear_vulnerabilidades_owasp,
    tool_verificar_integridad_cifrado_tls,
    tool_rotar_secretos_boveda
)

def get_hardening_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_escanear_vulnerabilidades_owasp,
            tool_verificar_integridad_cifrado_tls,
            tool_rotar_secretos_boveda
        ]
        builder = SargentoGraphBuilder(squad, squad_name="HardeningSargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
