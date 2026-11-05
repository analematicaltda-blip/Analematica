from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_ig_recibir_dm, tool_ig_responder_dm_info, tool_ig_enviar_link_inscripcion, tool_meta_asignar_asesor_humano, tool_meta_cerrar_ticket

def get_dms_privados_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_ig_recibir_dm, tool_ig_responder_dm_info, tool_ig_enviar_link_inscripcion, tool_meta_asignar_asesor_humano, tool_meta_cerrar_ticket]
        builder = SargentoGraphBuilder(squad, squad_name="DmsPrivadosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento DmsPrivadosSargento listo para el despliegue.")
    return build_sargento_agent
