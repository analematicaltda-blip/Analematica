"""
contable_general -> tenientes: teniente_partida_doble.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "teniente_partida_doble"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
