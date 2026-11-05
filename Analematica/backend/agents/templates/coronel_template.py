"""
Plantilla Base Canónica DEAA-V2.1: Coronel de División
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .capitan_template import CapitánBase

class CoronelBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la división estratégica")
    capitanes: List[CapitánBase] = Field(default_factory=list, description="Lista de capitanes de compañía")

    def ejecutar_orden_general(self, orden_general: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Descompone la orden macro del Estado Mayor en operaciones de compañía."""
        resultados_division = []
        for capitan in self.capitanes:
            res = capitan.ejecutar_plan_táctico(orden_general, params)
            resultados_division.append(res)
        return {
            "coronel": self.nombre,
            "mision_general": orden_general,
            "companias_desplegadas": len(self.capitanes),
            "reporte_consolidado": resultados_division
        }
