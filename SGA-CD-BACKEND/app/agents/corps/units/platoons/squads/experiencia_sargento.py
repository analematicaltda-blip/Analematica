from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_experiencia import ExperienciaSoldiers

def get_experiencia_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Experiencia.

    Este Sargento comanda a la escuadra responsable de la calidad de la interfaz de usuario.
    Recibe misiones para asegurar que la plataforma sea global y accesible, orquestando
    a los soldados de traducción (MILA) y de auditoría de accesibilidad.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados especialistas en UX
        squad = ExperienciaSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Internacionalización y UX", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Experiencia listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
