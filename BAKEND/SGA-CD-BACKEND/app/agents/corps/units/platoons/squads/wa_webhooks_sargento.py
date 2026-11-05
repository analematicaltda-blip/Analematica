from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_wa_validar_firma_hmac, tool_wa_parsear_mensaje, tool_wa_extraer_remitente, tool_wa_marcar_leido, tool_wa_enrutar_cola_ia

def get_wa_webhooks_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_wa_validar_firma_hmac, tool_wa_parsear_mensaje, tool_wa_extraer_remitente, tool_wa_marcar_leido, tool_wa_enrutar_cola_ia]
        builder = SargentoGraphBuilder(squad, squad_name="WaWebhooksSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento WaWebhooksSargento listo para el despliegue.")
    return build_sargento_agent
