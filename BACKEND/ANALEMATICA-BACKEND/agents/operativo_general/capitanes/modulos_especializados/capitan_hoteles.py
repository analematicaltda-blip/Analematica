"""
operativo_general -> capitanes/modulos_especializados: capitan_hoteles.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "capitan_hoteles"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
