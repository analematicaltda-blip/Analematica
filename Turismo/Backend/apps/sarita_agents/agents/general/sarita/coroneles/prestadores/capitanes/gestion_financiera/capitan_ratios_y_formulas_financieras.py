# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_financiera/capitan_ratios_y_formulas_financieras.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanRatiosYFormulasFinancieras(CapitanTemplate):
    """
    Agente de Indicadores: Calcula KPIs financieros de alto nivel (EBITDA, ROI, Liquidez).
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Indicadores): Generando reporte de ratios para misión {mision.id}")

        pasos = {
            "calculo_indicadores": {
                "descripcion": "Calcular indicadores de liquidez, rentabilidad y eficiencia.",
                "teniente": "roi_calculator", # Reutilizando teniente existente
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
        from apps.sarita_agents.tasks import TenienteROICalculator
        return {
            "roi_calculator": TenienteROICalculator()
        }
