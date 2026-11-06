from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_crm_completo import tool_enriquecer_tipo_entidad, tool_enriquecer_ubicacion_barrio, tool_enriquecer_participacion_previa, tool_enriquecer_preferencia_horario, tool_enriquecer_observaciones_asesor

def get_enriquecimiento_perfil_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_enriquecer_tipo_entidad, tool_enriquecer_ubicacion_barrio, tool_enriquecer_participacion_previa, tool_enriquecer_preferencia_horario, tool_enriquecer_observaciones_asesor]
        builder = SargentoGraphBuilder(squad, squad_name="EnriquecimientoPerfilSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento EnriquecimientoPerfilSargento listo para el despliegue.")
    return build_sargento_agent
