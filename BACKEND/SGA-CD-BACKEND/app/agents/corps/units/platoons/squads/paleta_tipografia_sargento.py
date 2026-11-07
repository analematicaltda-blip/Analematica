from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_aplicar_paleta_colores, tool_aplicar_fuente_titulos, tool_aplicar_fuente_cuerpo, tool_verificar_contraste_wcag, tool_insertar_marca_agua

def get_paleta_tipografia_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_aplicar_paleta_colores, tool_aplicar_fuente_titulos, tool_aplicar_fuente_cuerpo, tool_verificar_contraste_wcag, tool_insertar_marca_agua]
        builder = SargentoGraphBuilder(squad, squad_name="PaletaTipografiaSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento PaletaTipografiaSargento listo para el despliegue.")
    return build_sargento_agent
