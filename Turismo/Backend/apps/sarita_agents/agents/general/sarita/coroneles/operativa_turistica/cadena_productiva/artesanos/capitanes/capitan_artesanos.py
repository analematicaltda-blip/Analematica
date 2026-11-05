from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanArtesanos(CapitanTemplate):
    """
    Misión: Gestionar las operaciones específicas de los artesanos y sus productos.
    Fase 16: Cadena Productiva Turística.
    """

    def __init__(self, coronel):
        super().__init__(coronel=coronel)


    def _get_tenientes(self) -> Dict[str, Any]:
        from ..tenientes.teniente_artesano import TenienteArtesano
        return {"operativo_artesano": TenienteArtesano()}

    def plan(self, mision):
        """
        El corazón del Capitán. Diseña el plan táctico para el taller Artesano.
        """
        params = mision.directiva_original.get("parameters", {})
        # Enriquecer parámetros para el teniente
        params["mission_type"] = mision.directiva_original.get("mission", {}).get("type")
        params["user_id"] = mision.directiva_original.get("user_id")

        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {
            "1": {
                "teniente": "operativo_artesano",
                "descripcion": "Gestión operativa del taller (Negocio + Agentes)",
                "parametros": params
            }
        }
        p.save()
        return p
