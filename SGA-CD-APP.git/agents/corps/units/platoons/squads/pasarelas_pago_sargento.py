from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_generar_link_pago_online, tool_verificar_webhook_pago, tool_reintentar_cobro_fallido, tool_actualizar_factura_pagada, tool_enviar_comprobante_pago

def get_pasarelas_pago_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_generar_link_pago_online, tool_verificar_webhook_pago, tool_reintentar_cobro_fallido, tool_actualizar_factura_pagada, tool_enviar_comprobante_pago]
        builder = SargentoGraphBuilder(squad, squad_name="PasarelasPagoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PasarelasPagoSargento listo para el despliegue.")
    return build_sargento_agent
