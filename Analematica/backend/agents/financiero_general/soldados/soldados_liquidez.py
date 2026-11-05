"""
financiero_general -> soldados: soldados_liquidez.py
"""
from typing import Dict, Any, List

class AgentUnit:
    def __init__(self, name: str = "soldados_liquidez"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"unit": self.name, "status": "success", "payload": payload or {}}
