from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_cotizar_plan_mensual, tool_cotizar_paquete_familiar, tool_cotizar_convenio_colegio, tool_aplicar_cupon_descuento, tool_generar_cotizacion_pdf

def get_elaboracion_cotizaciones_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_cotizar_plan_mensual, tool_cotizar_paquete_familiar, tool_cotizar_convenio_colegio, tool_aplicar_cupon_descuento, tool_generar_cotizacion_pdf]
        builder = SargentoGraphBuilder(squad, squad_name="ElaboracionCotizacionesSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ElaboracionCotizacionesSargento listo para el despliegue.")
    return build_sargento_agent
