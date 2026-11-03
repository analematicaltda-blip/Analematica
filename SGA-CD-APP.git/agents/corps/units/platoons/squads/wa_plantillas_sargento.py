from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_wa_plantilla_recordatorio, tool_wa_plantilla_pago, tool_wa_mensaje_texto_simple, tool_wa_enviar_pdf, tool_wa_verificar_entrega

def get_wa_plantillas_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_wa_plantilla_recordatorio, tool_wa_plantilla_pago, tool_wa_mensaje_texto_simple, tool_wa_enviar_pdf, tool_wa_verificar_entrega]
        builder = SargentoGraphBuilder(squad, squad_name="WaPlantillasSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento WaPlantillasSargento listo para el despliegue.")
    return build_sargento_agent
