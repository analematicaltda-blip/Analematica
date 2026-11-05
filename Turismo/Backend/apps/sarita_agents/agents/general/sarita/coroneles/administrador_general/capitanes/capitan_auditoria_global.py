# backend/apps/sarita_agents/agents/general/sarita/coroneles/administrador_general/capitanes/capitan_auditoria_global.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from ..tenientes.tenienteauditoria_global import TenienteAuditoriaGlobal
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanAuditoriaGlobal(CapitanTemplate):
    """
    Capitán responsable de la auditoría global del sistema.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (AuditoriaGlobal): Planificando misión {mision.id}")

        parametros = mision.directiva_original.get("parameters", {})

        pasos = {
            "auditoria_general": {
                "descripcion": "Ejecutar revisión de logs y estados sistémicos.",
                "teniente": "auditoria_global",
                "parametros": parametros
            }
        }

        plan_tactico = PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )

        return plan_tactico

    def _get_tenientes(self) -> dict:
        return {
            "auditoria_global": TenienteAuditoriaGlobal()
        }
