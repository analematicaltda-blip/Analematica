from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_lead_duplicado_email, tool_lead_duplicado_telefono, tool_lead_fusionar_historial, tool_lead_actualizar_utm, tool_lead_crear_registro_pg

def get_deduplicacion_leads_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_lead_duplicado_email, tool_lead_duplicado_telefono, tool_lead_fusionar_historial, tool_lead_actualizar_utm, tool_lead_crear_registro_pg]
        builder = SargentoGraphBuilder(squad, squad_name="DeduplicacionLeadsSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento DeduplicacionLeadsSargento listo para el despliegue.")
    return build_sargento_agent
