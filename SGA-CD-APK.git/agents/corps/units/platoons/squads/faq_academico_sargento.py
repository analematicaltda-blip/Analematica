from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_faq_horarios, tool_faq_tarifas, tool_faq_sedes, tool_faq_requisitos, tool_faq_eventos

def get_faq_academico_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_faq_horarios, tool_faq_tarifas, tool_faq_sedes, tool_faq_requisitos, tool_faq_eventos]
        builder = SargentoGraphBuilder(squad, squad_name="FaqAcademicoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento FaqAcademicoSargento listo para el despliegue.")
    return build_sargento_agent
