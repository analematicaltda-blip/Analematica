from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_detectar_queja_pqr, tool_escalar_urgente, tool_registrar_pqr_db, tool_notificacion_push_directores, tool_generar_radicado

def get_escalacion_pqrs_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_detectar_queja_pqr, tool_escalar_urgente, tool_registrar_pqr_db, tool_notificacion_push_directores, tool_generar_radicado]
        builder = SargentoGraphBuilder(squad, squad_name="EscalacionPqrsSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento EscalacionPqrsSargento listo para el despliegue.")
    return build_sargento_agent
