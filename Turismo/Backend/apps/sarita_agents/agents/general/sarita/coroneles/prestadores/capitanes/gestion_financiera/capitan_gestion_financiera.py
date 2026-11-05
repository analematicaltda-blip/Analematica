# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_financiera/capitan_gestion_financiera.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanGestionFinanciera(CapitanTemplate):
    """
    Agente Financiero: Orquesta los movimientos de fondos y la conciliación bancaria.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Financiero): Planificando movimiento para misión {mision.id}")

        pasos = {
            "movimiento_fondos": {
                "descripcion": "Registrar ingreso o egreso en el ERP financiero.",
                "teniente": "admin_persistencia_financiera",
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
        from apps.sarita_agents.agents.general.sarita.coroneles.administrador_general.tenientes.operativos.tenientes_persistencia import AdminTenientePersistenciaFinanciera
        return {
            "admin_persistencia_financiera": AdminTenientePersistenciaFinanciera()
        }
