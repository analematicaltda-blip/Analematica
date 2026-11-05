import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOperacionNocturna(CapitanTemplate):
    """
    Capitán responsable de la ejecución táctica en Bares y Discotecas.
    """
    def _get_tenientes(self) -> dict:
        return {
            "teniente_nocturno": "teniente_nocturno"
        }

    def plan(self, mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Nocturno): Creando plan para misión {mision.id}")

        params = mision.directiva_original.get("parameters", {})
        # Enriquecer parámetros con el tipo de acción para el teniente
        m_type = mision.directiva_original.get("mission", {}).get("type")
        if not m_type:
            m_type = mision.directiva_original.get("action")
        params["action"] = m_type

        pasos = {
            "1": {
                "teniente": "teniente_nocturno",
                "descripcion": f"Ejecutar acción: {m_type}",
                "parametros": params
            }
        }

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )
