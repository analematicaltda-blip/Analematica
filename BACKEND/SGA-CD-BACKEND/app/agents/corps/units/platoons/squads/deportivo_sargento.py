from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_deportivo import DeportivoSoldiers

def get_deportivo_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento Deportivo.

    Este Sargento recibe misiones de su Teniente relacionadas con la gestión deportiva.
    Utiliza a su escuadra de Soldados para crear entrenamientos, asignar entrenadores,
    reservar escenarios y gestionar inscripciones y asistencia.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas
        squad = DeportivoSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Deportivo", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento Deportivo listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
