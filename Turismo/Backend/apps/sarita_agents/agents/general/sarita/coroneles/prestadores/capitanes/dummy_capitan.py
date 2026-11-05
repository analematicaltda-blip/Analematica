# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/dummy_capitan.py
from .....capitan_template import CapitanTemplate
from ...tenientes.dummy_teniente import DummyTeniente
from ......models import Mision, PlanTáctico

class DummyCapitan(CapitanTemplate):
    """
    Un capitán de marcador de posición que se integra con la capa de persistencia.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        """
        Crea un plan táctico simulado y lo persiste.
        """
        print(f"DUMMY CAPITÁN: Creando plan para misión {mision.id}")

        pasos = {
            "paso_1": {
                "descripcion": "Ejecutar tarea simulada 1",
                "teniente": "dummy",
                "parametros": {"param1": "valor1"}
            }
        }

        plan_tactico = PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos
        )

        return plan_tactico

    def _get_tenientes(self) -> dict:
        """
        Carga el roster de Tenientes para este Capitán.
        """
        return {
            "dummy": DummyTeniente()
        }
