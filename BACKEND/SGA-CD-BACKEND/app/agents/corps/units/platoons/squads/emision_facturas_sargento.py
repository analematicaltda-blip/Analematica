from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_factura_matricula_db, tool_factura_mensualidad_db, tool_aplicar_recargos_descuentos, tool_recibo_caja_efectivo, tool_nota_credito_anulacion

def get_emision_facturas_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_factura_matricula_db, tool_factura_mensualidad_db, tool_aplicar_recargos_descuentos, tool_recibo_caja_efectivo, tool_nota_credito_anulacion]
        builder = SargentoGraphBuilder(squad, squad_name="EmisionFacturasSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento EmisionFacturasSargento listo para el despliegue.")
    return build_sargento_agent
