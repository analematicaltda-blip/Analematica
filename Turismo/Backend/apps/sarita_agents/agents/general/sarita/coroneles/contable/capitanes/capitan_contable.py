# backend/apps/sarita_agents/agents/general/sarita/coroneles/contable/capitanes/capitan_contable.py

from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico
import logging

logger = logging.getLogger(__name__)

class CapitanContable(CapitanTemplate):
    """
    NIVEL 3 — CAPITÁN CONTABLE
    Diseña planes tácticos y divide misiones en tareas operativas.
    """
    def _get_tenientes(self) -> dict:
        from ..tenientes.teniente_registro import TenienteRegistroContable
        return {
            "registro_contable": TenienteRegistroContable()
        }

    def plan(self, mision):
        logger.info(f"CAPITÁN CONTABLE: Planificando misión {mision.id}")

        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)

        # El plan incluye la supervisión técnica del Teniente de Registro
        p.pasos_del_plan = {
            "1": {
                "teniente": "registro_contable",
                "descripcion": "Validación y registro de transacciones contables.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p
