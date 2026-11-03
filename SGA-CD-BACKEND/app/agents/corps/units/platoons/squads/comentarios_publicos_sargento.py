from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_meta_obtener_comentarios, tool_meta_filtrar_spam, tool_meta_responder_comentario, tool_meta_ocultar_inapropiado, tool_meta_like_comentario

def get_comentarios_publicos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_meta_obtener_comentarios, tool_meta_filtrar_spam, tool_meta_responder_comentario, tool_meta_ocultar_inapropiado, tool_meta_like_comentario]
        builder = SargentoGraphBuilder(squad, squad_name="ComentariosPublicosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ComentariosPublicosSargento listo para el despliegue.")
    return build_sargento_agent
