# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/onboarding_prestador_capitan.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from ..tenientes.validacion_prestador_teniente import TenienteValidacionPrestador
from ..tenientes.persistencia_prestador_teniente import TenientePersistenciaPrestador
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOnboardingPrestador(CapitanTemplate):
    """
    Capitán especializado en el proceso de onboarding de nuevos Prestadores.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        """
        Crea el plan táctico para registrar un nuevo prestador.
        El plan consiste en dos pasos: validar los datos y luego persistirlos.
        """
        logger.info(f"CAPITÁN (OnboardingPrestador): Creando plan para misión {mision.id}")

        datos_prestador = mision.directiva_original.get("mission", {}).get("datos", {})

        pasos = {
            "paso_1_validacion": {
                "descripcion": "Validar los datos básicos del nuevo prestador.",
                "teniente": "validacion",
                "parametros": datos_prestador
            },
            "paso_2_persistencia": {
                "descripcion": "Crear el registro del nuevo prestador en la base de datos.",
                "teniente": "persistencia",
                "parametros": datos_prestador
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
        Carga el roster de Tenientes bajo el mando de este Capitán.
        """
        return {
            "validacion": TenienteValidacionPrestador(),
            "persistencia": TenientePersistenciaPrestador()
        }
