from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_enviar_cotizacion_multicanal, tool_verificar_lectura_propuesta, tool_programar_seguimiento, tool_ajustar_contraoferta, tool_vencer_cotizacion_vigencia

def get_seguimiento_propuestas_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_enviar_cotizacion_multicanal, tool_verificar_lectura_propuesta, tool_programar_seguimiento, tool_ajustar_contraoferta, tool_vencer_cotizacion_vigencia]
        builder = SargentoGraphBuilder(squad, squad_name="SeguimientoPropuestasSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento SeguimientoPropuestasSargento listo para el despliegue.")
    return build_sargento_agent
