"""
Plantilla Base Canónica DEAA-V2.1: Soldado Atómico
"""
from typing import Dict, Any, Callable
from pydantic import BaseModel, Field

class SoldadoBase(BaseModel):
    nombre: str = Field(..., description="Identificador único del soldado especialista")
    especialidad: str = Field(..., description="Área técnica atómica de ejecución")

    def ejecutar_accion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una acción física atómica, determinista y reversible."""
        return {
            "soldado": self.nombre,
            "especialidad": self.especialidad,
            "resultado": "OK",
            "detalles": params
        }
