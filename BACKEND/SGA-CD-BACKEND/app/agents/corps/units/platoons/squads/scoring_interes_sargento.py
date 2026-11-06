from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_score_interes_deporte, tool_score_interes_cultura, tool_score_tamano_familia, tool_score_proximidad_sede, tool_score_clasificacion_temperatura

def get_scoring_interes_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_score_interes_deporte, tool_score_interes_cultura, tool_score_tamano_familia, tool_score_proximidad_sede, tool_score_clasificacion_temperatura]
        builder = SargentoGraphBuilder(squad, squad_name="ScoringInteresSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ScoringInteresSargento listo para el despliegue.")
    return build_sargento_agent
