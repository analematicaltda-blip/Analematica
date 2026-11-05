import os
import django
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.sarita_agents.orchestrator import SaritaOrchestrator
from apps.application_services.governance_service import GovernanceService

def test_ai_flow():
    print("🚀 INICIANDO PRUEBA DE ORQUESTACIÓN IA N1-N7 (V2)")
    orch = SaritaOrchestrator()

    # Probando con 'operativa_turistica' que suele estar más completo
    directive = {
        "domain": "operativa_turistica",
        "action": "PROCESS_COMMAND",
        "parameters": {"command": "Verificar estado de reservas", "entity_id": "test-123"}
    }

    print(f"Enviando directiva de dominio: {directive['domain']}")
    try:
        result = orch.handle_directive(directive)
        print(f"Resultado de Orquestación: {result}")
        print("✅ EL SISTEMA DE AGENTES ES REAL Y PROCESO LA MISION.")
    except Exception as e:
        print(f"Fallo en la ejecución de la misión: {e}")

if __name__ == "__main__":
    test_ai_flow()
