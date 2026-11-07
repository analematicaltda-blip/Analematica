# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/dummy_teniente.py
from .....teniente_template import TenienteTemplate

class DummyTeniente(TenienteTemplate):
    """
    Un teniente de marcador de posición para probar la ejecución.
    """
    def perform_action(self, parametros: dict):
        """
        Simula la ejecución de una acción.
        """
        print(f"DUMMY TENIENTE: Realizando acción simulada con parámetros: {parametros}")
        return {"status": "ok", "message": "Tarea dummy ejecutada."}
