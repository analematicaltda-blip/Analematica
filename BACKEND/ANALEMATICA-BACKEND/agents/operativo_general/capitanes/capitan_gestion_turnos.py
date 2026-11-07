"""
operativo_general -> capitanes: capitan_gestion_turnos.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "capitan_gestion_turnos"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
