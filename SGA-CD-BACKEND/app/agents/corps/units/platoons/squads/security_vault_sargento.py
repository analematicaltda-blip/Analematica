from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_gobernanza_seguridad import (
    tool_cifrar_clave_boveda,
    tool_registrar_evento_star
)

def get_security_vault_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_cifrar_clave_boveda,
            tool_registrar_evento_star
        ]
        builder = SargentoGraphBuilder(squad, squad_name="SecurityVaultSargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
