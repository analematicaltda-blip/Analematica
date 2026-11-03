from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_convertir_a_alumno, tool_crear_usuario_alumno, tool_vincular_acudiente, tool_generar_contrato_digital, tool_firma_digital_terminos

def get_formalizacion_matricula_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_convertir_a_alumno, tool_crear_usuario_alumno, tool_vincular_acudiente, tool_generar_contrato_digital, tool_firma_digital_terminos]
        builder = SargentoGraphBuilder(squad, squad_name="FormalizacionMatriculaSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento FormalizacionMatriculaSargento listo para el despliegue.")
    return build_sargento_agent
