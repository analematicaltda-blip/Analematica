from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from typing import Dict, Any

class CapitanSEOTuristico(CapitanTemplate):
    """
    Misión: Optimizar la visibilidad orgánica de los prestadores en motores de búsqueda
    y dentro de la plataforma Sarita.
    """
    def _get_tenientes(self) -> dict:
        return {
            "seo_technical": "seo_technical",
            "content_optimization": "content_optimization"
        }

    def plan(self, mision):
        plan_tactico = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan_tactico.pasos_del_plan = {
            "paso_1": {"teniente": "seo_technical", "descripcion": "Auditoría técnica SEO", "parametros": {}},
            "paso_2": {"teniente": "content_optimization", "descripcion": "Optimización de keywords turísticas", "parametros": {}}
        }
        plan_tactico.save()
        return plan_tactico
