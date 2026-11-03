from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_render_slides_secuencia, tool_paginacion_badge, tool_empaquetar_directorio, tool_generar_pdf_carrusel, tool_verificar_resolucion_slides

def get_empaquetado_carrusel_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_render_slides_secuencia, tool_paginacion_badge, tool_empaquetar_directorio, tool_generar_pdf_carrusel, tool_verificar_resolucion_slides]
        builder = SargentoGraphBuilder(squad, squad_name="EmpaquetadoCarruselSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento EmpaquetadoCarruselSargento listo para el despliegue.")
    return build_sargento_agent
