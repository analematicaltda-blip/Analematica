from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_agendar_llamada_contacto, tool_enviar_email_bienvenida, tool_recordatorio_asesor, tool_registrar_intento_contacto, tool_actualizar_pipeline_contactado

def get_agendamiento_contacto_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_agendar_llamada_contacto, tool_enviar_email_bienvenida, tool_recordatorio_asesor, tool_registrar_intento_contacto, tool_actualizar_pipeline_contactado]
        builder = SargentoGraphBuilder(squad, squad_name="AgendamientoContactoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AgendamientoContactoSargento listo para el despliegue.")
    return build_sargento_agent
