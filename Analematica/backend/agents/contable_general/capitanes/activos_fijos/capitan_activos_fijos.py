"""
contable_general -> capitanes/activos_fijos: capitan_activos_fijos.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "capitan_activos_fijos"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
