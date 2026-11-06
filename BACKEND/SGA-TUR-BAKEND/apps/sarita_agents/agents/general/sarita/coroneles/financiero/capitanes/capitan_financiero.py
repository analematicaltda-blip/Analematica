# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/capitanes/capitan_financiero.py

from apps.sarita_agents.agents.capitan_template import CapitanTemplate
import logging

logger = logging.getLogger(__name__)

class CapitanFinanciero(CapitanTemplate):
    """
    NIVEL 3 — CAPITÁN FINANCIERO
    Diseña planes de optimización de recursos y supervisa la salud financiera.
    """
    def _get_tenientes(self) -> dict:
        from ..tenientes.teniente_tesoreria import TenienteTesoreria
        return {
            "tesoreria": TenienteTesoreria()
        }

    def plan(self, mision):
        logger.info(f"CAPITÁN FINANCIERO: Planificando misión {mision.id}")
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)

        p.pasos_del_plan = {
            "1": {
                "teniente": "tesoreria",
                "descripcion": "Gestión de tesorería y análisis de indicadores.",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        p.save()
        return p
