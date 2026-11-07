from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_fb_publicar_video, tool_fb_publicar_post, tool_in_autenticar_urn, tool_in_publicar_articulo, tool_in_subir_carrusel_pdf

def get_meta_linkedin_pub_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_fb_publicar_video, tool_fb_publicar_post, tool_in_autenticar_urn, tool_in_publicar_articulo, tool_in_subir_carrusel_pdf]
        builder = SargentoGraphBuilder(squad, squad_name="MetaLinkedinPubSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento MetaLinkedinPubSargento listo para el despliegue.")
    return build_sargento_agent
