from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_sistemas_legal_seo import (
    tool_auditar_seo_onpage,
    tool_generar_sitemap_dinamico,
    tool_validar_cumplimiento_habeas_data,
    tool_auditar_terminos_y_privacidad
)

def get_seo_legal_sargento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [
            tool_auditar_seo_onpage,
            tool_generar_sitemap_dinamico,
            tool_validar_cumplimiento_habeas_data,
            tool_auditar_terminos_y_privacidad
        ]
        builder = SargentoGraphBuilder(squad, squad_name="SeoLegalSargento", llm=llm)
        return builder.build_graph()

    return build_sargento_agent
