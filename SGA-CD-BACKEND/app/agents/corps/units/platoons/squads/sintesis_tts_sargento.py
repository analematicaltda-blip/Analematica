from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_tts_voz_femenina, tool_tts_voz_masculina, tool_tts_ajustar_velocidad, tool_tts_modular_tono, tool_tts_limpiar_ruido

def get_sintesis_tts_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_tts_voz_femenina, tool_tts_voz_masculina, tool_tts_ajustar_velocidad, tool_tts_modular_tono, tool_tts_limpiar_ruido]
        builder = SargentoGraphBuilder(squad, squad_name="SintesisTtsSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento SintesisTtsSargento listo para el despliegue.")
    return build_sargento_agent
