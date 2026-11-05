from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_seguridad import SeguridadSoldiers

def get_seguridad_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Seguridad y Auditoría.

    Este Sargento utiliza a su escuadra para ejecutar auditorías de permisos,
    registrar eventos críticos y verificar la seguridad de los datos.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas
        squad = SeguridadSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Seguridad y Auditoría", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Seguridad listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
