from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from app.tools.herramientas_institucional import InstitucionalSoldiers

def get_institucional_sargento_graph(llm: any):
    """
    Construye y devuelve el agente Sargento de Gestión Institucional.

    Este Sargento es el administrador de la plataforma. Recibe misiones para
    expandir el sistema creando nuevos inquilinos (sedes), organizando las áreas,
    gestionando el personal y manteniendo actualizado el sitio web público.
    """

    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        api_client = state["app_context"].api
        # El Sargento recluta a su escuadra de soldados administradores
        squad = InstitucionalSoldiers(api_client).get_all_soldiers()
        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Gestión Institucional", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión Institucional listo para el despliegue.")

    # Se devuelve la función constructora para ser utilizada por el Teniente.
    return build_sargento_agent
