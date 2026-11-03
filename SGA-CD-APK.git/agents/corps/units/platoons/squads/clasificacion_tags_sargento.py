from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_asignar_uuid_asset, tool_categorizar_medio_deporte, tool_extraer_exif_metadata, tool_asignar_tags_busqueda, tool_registrar_inquilino_propietario

def get_clasificacion_tags_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_asignar_uuid_asset, tool_categorizar_medio_deporte, tool_extraer_exif_metadata, tool_asignar_tags_busqueda, tool_registrar_inquilino_propietario]
        builder = SargentoGraphBuilder(squad, squad_name="ClasificacionTagsSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento ClasificacionTagsSargento listo para el despliegue.")
    return build_sargento_agent
