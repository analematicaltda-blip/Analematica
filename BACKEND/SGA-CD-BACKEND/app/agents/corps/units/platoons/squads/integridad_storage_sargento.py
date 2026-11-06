from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_multimedia_completo import tool_calcular_sha256_media, tool_verificar_integridad_bitstream, tool_detectar_duplicados_storage, tool_reparar_moov_atom_mp4, tool_cuarentena_corruptos

def get_integridad_storage_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [tool_calcular_sha256_media, tool_verificar_integridad_bitstream, tool_detectar_duplicados_storage, tool_reparar_moov_atom_mp4, tool_cuarentena_corruptos]
        builder = SargentoGraphBuilder(squad, squad_name="IntegridadStorageSargento", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento IntegridadStorageSargento listo para el despliegue.")
    return build_sargento_agent
