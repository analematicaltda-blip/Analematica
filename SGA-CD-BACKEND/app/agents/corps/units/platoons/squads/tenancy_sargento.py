from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_gobernanza_seguridad import (
    tool_crear_particion_inquilino,
    tool_auditar_cuotas_recursos,
    tool_asignar_politica_rbac
)

def get_tenancy_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_crear_particion_inquilino,
            tool_auditar_cuotas_recursos,
            tool_asignar_politica_rbac
        ]
        builder = SargentoGraphBuilder(squad, squad_name="TenancySargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
