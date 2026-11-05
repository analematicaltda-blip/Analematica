from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class CapitanContabilidadGeneral(CapitanTemplate):
    """
    Misión: Orquestar el ciclo contable completo, asegurando la integridad
    de los registros, el cumplimiento normativo y la correcta generación
    de informes financieros.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        """
        Crea el plan táctico para la gestión contable.
        """
        logger.info(f"CAPITÁN (ContabilidadGeneral): Creando plan para misión {mision.id}")

        pasos = {
            "paso_1_registro": {
                "descripcion": "Registrar transacciones en el libro diario.",
                "teniente": "admin_persistencia_contable", # Reutilizando teniente estabilizado
                "parametros": mision.directiva_original.get("parameters", {})
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
        """
        Carga el roster de Tenientes.
        """
        from apps.sarita_agents.agents.general.sarita.coroneles.administrador_general.tenientes.operativos.tenientes_persistencia import AdminTenientePersistenciaContable
        return {
            "admin_persistencia_contable": AdminTenientePersistenciaContable()
        }
