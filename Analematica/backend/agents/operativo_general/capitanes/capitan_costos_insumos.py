"""
operativo_general -> capitanes: capitan_costos_insumos.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "capitan_costos_insumos"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
