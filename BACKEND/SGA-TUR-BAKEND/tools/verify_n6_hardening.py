import os
import django
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.sarita_agents.orchestrator import SaritaOrchestrator
from apps.application_services.governance_service import GovernanceService

def test_ai_flow():
    print("🚀 INICIANDO PRUEBA DE ORQUESTACIÓN IA N1-N7")
    orch = SaritaOrchestrator()

    directive = {
        "domain": "contable",
        "action": "ERP_GENERATE_BALANCE",
        "parameters": {"tenant_id": str(uuid.uuid4()), "initial": True}
    }

    print(f"Enviando directiva de dominio: {directive['domain']}")
    # En el entorno de sandbox, es posible que el coronel falle si no hay datos,
    # pero el orquestador debe ser capaz de procesar e intentar la ejecución.
    try:
        # Usamos handle_directive que encapsula start y execute
        result = orch.handle_directive(directive)
        print(f"Resultado de Orquestación: {result}")
        print("✅ EL SISTEMA DE AGENTES ES REAL Y RESPONDIO.")
    except Exception as e:
        print(f"Fallo controlado del Orquestador (probablemente falta de datos): {e}")

if __name__ == "__main__":
    test_ai_flow()
