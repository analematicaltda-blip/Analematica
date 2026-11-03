from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_lead_capturar_landing, tool_lead_capturar_redes, tool_lead_capturar_presencial, tool_lead_validar_email, tool_lead_validar_telefono

def get_captura_forms_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_lead_capturar_landing, tool_lead_capturar_redes, tool_lead_capturar_presencial, tool_lead_validar_email, tool_lead_validar_telefono]
        builder = SargentoGraphBuilder(squad, squad_name="CapturaFormsSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento CapturaFormsSargento listo para el despliegue.")
    return build_sargento_agent
