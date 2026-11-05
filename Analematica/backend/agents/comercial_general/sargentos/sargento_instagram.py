"""
comercial_general -> sargentos: sargento_instagram.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "sargento_instagram"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
