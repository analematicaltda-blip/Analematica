from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_inteligencia import InteligenciaSoldiers

def get_inteligencia_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Inteligencia.

    Este Sargento comanda a la escuadra de analítica y soporte de IA. Recibe misiones
    para generar reportes, construir dashboards, o utilizar al agente de IA.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas en datos e IA
        squad = InteligenciaSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Inteligencia y Apoyo", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Inteligencia listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
