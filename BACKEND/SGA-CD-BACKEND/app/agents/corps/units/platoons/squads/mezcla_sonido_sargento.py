from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_seleccionar_musica_fondo, tool_mezclar_voz_musica, tool_normalizar_lufs, tool_agregar_efectos_sfx, tool_audio_fade_in_out

def get_mezcla_sonido_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_seleccionar_musica_fondo, tool_mezclar_voz_musica, tool_normalizar_lufs, tool_agregar_efectos_sfx, tool_audio_fade_in_out]
        builder = SargentoGraphBuilder(squad, squad_name="MezclaSonidoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento MezclaSonidoSargento listo para el despliegue.")
    return build_sargento_agent
