from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_redes_completo import tool_sentimiento_polaridad, tool_sentimiento_keywords, tool_sentimiento_insatisfaccion, tool_sentimiento_interes_compra, tool_sentimiento_indice_salud

def get_analisis_sentimiento_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_sentimiento_polaridad, tool_sentimiento_keywords, tool_sentimiento_insatisfaccion, tool_sentimiento_interes_compra, tool_sentimiento_indice_salud]
        builder = SargentoGraphBuilder(squad, squad_name="AnalisisSentimientoSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AnalisisSentimientoSargento listo para el despliegue.")
    return build_sargento_agent
