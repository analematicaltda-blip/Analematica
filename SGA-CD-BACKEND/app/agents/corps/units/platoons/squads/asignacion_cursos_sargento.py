from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_inscribir_grupo_entrenamiento, tool_inscribir_taller_cultural, tool_verificar_requisitos_salud, tool_asignar_kit_uniforme, tool_enviar_kit_bienvenida

def get_asignacion_cursos_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_inscribir_grupo_entrenamiento, tool_inscribir_taller_cultural, tool_verificar_requisitos_salud, tool_asignar_kit_uniforme, tool_enviar_kit_bienvenida]
        builder = SargentoGraphBuilder(squad, squad_name="AsignacionCursosSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento AsignacionCursosSargento listo para el despliegue.")
    return build_sargento_agent
