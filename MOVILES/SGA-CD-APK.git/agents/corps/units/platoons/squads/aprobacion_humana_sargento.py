from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_crear_orden_pendiente_aprobacion, tool_verificar_firma_admin, tool_revocar_orden_bloqueada, tool_notificar_vobo_admin, tool_auditoria_quien_aprobo

def get_aprobacion_humana_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_crear_orden_pendiente_aprobacion, tool_verificar_firma_admin, tool_revocar_orden_bloqueada, tool_notificar_vobo_admin, tool_auditoria_quien_aprobo]
        builder = SargentoGraphBuilder(squad, squad_name="AprobacionHumanaSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AprobacionHumanaSargento listo para el despliegue.")
    return build_sargento_agent
