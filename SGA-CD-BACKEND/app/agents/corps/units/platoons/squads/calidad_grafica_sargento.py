from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_optimizar_peso_imagen, tool_convertir_png_jpg_webp, tool_verificar_dpi, tool_variacion_modo_oscuro, tool_archivar_master_grafico

def get_calidad_grafica_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_optimizar_peso_imagen, tool_convertir_png_jpg_webp, tool_verificar_dpi, tool_variacion_modo_oscuro, tool_archivar_master_grafico]
        builder = SargentoGraphBuilder(squad, squad_name="CalidadGraficaSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento CalidadGraficaSargento listo para el despliegue.")
    return build_sargento_agent
