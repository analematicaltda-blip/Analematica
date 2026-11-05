from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_gamificacion import GamificacionSoldiers

def get_gamificacion_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Gamificación (SIGA).

    Este Sargento recibe misiones relacionadas con la motivación y recompensas.
    Utiliza a su escuadra para asignar puntos, medallas, actualizar niveles y
    gestionar los rankings.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas en SIGA
        squad = GamificacionSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Gamificación (SIGA)", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gamificación listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
