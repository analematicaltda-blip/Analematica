# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_archivistica/capitan_integridad_documental.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanIntegridadDocumental(CapitanTemplate):
    """
    Agente de Integridad: Garantiza que los documentos no hayan sido alterados.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Integridad): Verificando integridad para misión {mision.id}")

        pasos = {
            "verificacion_hash": {
                "descripcion": "Validar hashes SHA-256 y trazabilidad Blockchain.",
                "teniente": "archivistico_integridad",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )

    def _get_tenientes(self) -> dict:
        return {
            "archivistico_integridad": "archivistico_integridad"
        }
