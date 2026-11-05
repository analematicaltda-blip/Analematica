# backend/apps/sarita_agents/finanzas/capitan_cac.py
import logging
from ..agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
from apps.finanzas.models import FinancialEventRecord # DECOUPLED (TODO: Move to FinancialService)
from django.db.models import Sum

logger = logging.getLogger(__name__)

class CapitanCAC(CapitanTemplate):
    """
    Capitán CAC: Calcula el Costo de Adquisición.
    """
    def _get_tenientes(self) -> dict:
        return {
            "calculator": "cac_calculator" # Se debe registrar en tasks.py
        }

    def plan(self, mision: Mision) -> PlanTáctico:
        session_id = mision.directiva_original.get("parameters", {}).get("session_id")

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan={
                "1": {
                    "teniente": self.tenientes["calculator"],
                    "descripcion": "Calcular CAC de sesión",
                    "parametros": {"session_id": session_id}
                }
            }
        )

    def calculate_cac(self, session_id):
        """Lógica directa para uso rápido."""
        events = FinancialEventRecord.objects.filter(session_id=session_id)
        # CAC = costo_IA + tiempo_agente + costo_infraestructura
        # Asumimos valores por minuto
        costo_ia_por_minuto = 0.05
        costo_infra_fijo = 0.10

        minutos = events.filter(event_type='voice_minute_consumed').count()
        total_cac = (minutos * costo_ia_por_minuto) + costo_infra_fijo

        return total_cac
