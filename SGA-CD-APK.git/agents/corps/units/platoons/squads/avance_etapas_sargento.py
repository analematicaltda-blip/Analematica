from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_pipeline_etapa_diagnostico, tool_pipeline_etapa_propuesta, tool_pipeline_etapa_negociacion, tool_pipeline_marcar_ganada, tool_pipeline_marcar_perdida

def get_avance_etapas_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_pipeline_etapa_diagnostico, tool_pipeline_etapa_propuesta, tool_pipeline_etapa_negociacion, tool_pipeline_marcar_ganada, tool_pipeline_marcar_perdida]
        builder = SargentoGraphBuilder(squad, squad_name="AvanceEtapasSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AvanceEtapasSargento listo para el despliegue.")
    return build_sargento_agent
