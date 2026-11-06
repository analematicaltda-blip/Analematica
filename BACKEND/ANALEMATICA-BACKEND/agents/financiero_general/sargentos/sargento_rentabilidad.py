"""
financiero_general -> sargentos: sargento_rentabilidad.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "sargento_rentabilidad"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
