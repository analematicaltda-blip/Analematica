# backend/apps/sarita_agents/agents/marketing/capitan_embudo.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanEmbudo(CapitanTemplate):
    """
    Capitán Comercial de Embudo: Lleva la conversación y decide la ruta del prospecto.
    """
    def _get_tenientes(self) -> dict:
        return {
            "calificacion": "marketing_calificacion",
            "dolor": "marketing_dolor",
            "oferta": "marketing_oferta",
            "objeciones": "marketing_objeciones",
            "cierre": "marketing_cierre"
        }

    def plan(self, mision: Mision) -> PlanTáctico:
        directiva = mision.directiva_original
        text = directiva.get("voice_context", {}).get("original_text", "")

        # El plan para el embudo es secuencial o basado en el estado de la conversación.
        # Phase 4-M simplificada: ejecutamos calificacion y dolor en paralelo.

        pasos = {
            "1": {
                "teniente": self.tenientes["calificacion"],
                "descripcion": "Calificar prospecto",
                "parametros": {"text": text}
            },
            "2": {
                "teniente": self.tenientes["dolor"],
                "descripcion": "Detectar dolor principal",
                "parametros": {"text": text}
            }
        }

        # Si ya tenemos calificacion, podríamos pasar a oferta
        if directiva.get("context", {}).get("tipo_usuario"):
            pasos["3"] = {
                "teniente": self.tenientes["oferta"],
                "descripcion": "Generar oferta",
                "parametros": directiva.get("context")
            }

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos
        )
