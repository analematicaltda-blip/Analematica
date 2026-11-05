from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_identificar_contratos_30d, tool_oferta_renovacion_anticipada, tool_beneficio_antiguedad, tool_reenganche_alumnos_antiguos, tool_oferta_retorno_especial

def get_campanas_renovacion_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_identificar_contratos_30d, tool_oferta_renovacion_anticipada, tool_beneficio_antiguedad, tool_reenganche_alumnos_antiguos, tool_oferta_retorno_especial]
        builder = SargentoGraphBuilder(squad, squad_name="CampanasRenovacionSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento CampanasRenovacionSargento listo para el despliegue.")
    return build_sargento_agent
