"""
comercial_general -> sargentos: sargento_whatsapp.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "sargento_whatsapp"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
