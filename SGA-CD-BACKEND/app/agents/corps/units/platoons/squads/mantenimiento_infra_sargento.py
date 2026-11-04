from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_sistemas_legal_seo import (
    tool_ejecutar_mantenimiento_db,
    tool_purgar_cache_y_logs
)

def get_mantenimiento_infra_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_ejecutar_mantenimiento_db,
            tool_purgar_cache_y_logs
        ]
        builder = SargentoGraphBuilder(squad, squad_name="MantenimientoInfraSargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
