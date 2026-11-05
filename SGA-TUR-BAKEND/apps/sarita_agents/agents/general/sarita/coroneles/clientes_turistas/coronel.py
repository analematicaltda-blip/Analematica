# backend/apps/sarita_agents/agents/general/sarita/coroneles/clientes_turistas/coronel.py

from .....coronel_template import CoronelTemplate
from .capitanes.capitan_experiencia_turista import CapitanExperienciaTurista
from .capitanes.capitan_reservas_turista import CapitanReservasTurista
from .capitanes.capitan_busqueda_servicios import CapitanBusquedaServicios
from .capitanes.capitan_pqrs import CapitanPqrs
from .capitanes.capitan_gestion_perfil import CapitanGestionPerfil
from .capitanes.capitan_contexto_viaje import CapitanContextoViaje

class ClientesTuristasCoronel(CoronelTemplate):
    """
    Coronel de Atención al Turista (Vía 3).
    Gestiona la experiencia del cliente final, desde la búsqueda hasta el post-viaje.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="clientes_turistas")

    def _get_capitanes(self) -> dict:
        return {
            "experiencia": CapitanExperienciaTurista(coronel=self),
            "reservas": CapitanReservasTurista(coronel=self),
            "busqueda": CapitanBusquedaServicios(coronel=self),
            "pqrs": CapitanPqrs(coronel=self),
            "perfil": CapitanGestionPerfil(coronel=self),
            "contexto": CapitanContextoViaje(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")

        mapping = {
            "FIND_ACCOMMODATION": "busqueda",
            "BOOK_SERVICE": "reservas",
            "FILE_COMPLAINT": "pqrs",
            "GET_PERSONALIZED_ITINERARY": "experiencia",
            "UPDATE_TRAVELER_PREFERENCES": "perfil",
        }

        return self.capitanes.get(mapping.get(m_type))
