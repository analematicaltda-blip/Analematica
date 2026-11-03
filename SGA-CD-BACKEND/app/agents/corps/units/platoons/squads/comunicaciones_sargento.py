from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_comunicaciones import ComunicacionesSoldiers

def get_comunicaciones_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Comunicaciones.

    Este Sargento recibe misiones de su Teniente relacionadas con la interacción directa
    con los usuarios. Orquesta a su escuadra para enviar notificaciones, programar
    recordatorios y facilitar la comunicación interna.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas en comunicación
        squad = ComunicacionesSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Comunicación y Notificaciones", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Comunicaciones listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
