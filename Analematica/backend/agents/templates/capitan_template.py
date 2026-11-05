"""
Plantilla Base Canónica DEAA-V2.1: Capitán de Compañía
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .teniente_template import TenienteBase

class CapitánBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la compañía")
    tenientes: List[TenienteBase] = Field(default_factory=list, description="Lista de tenientes coordinados")

    def ejecutar_plan_táctico(self, orden_coronel: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Descompone la orden del Coronel en fases de pelotón secuenciales."""
        informes = []
        for teniente in self.tenientes:
            inf = teniente.coordinar_peloton(orden_coronel, params)
            informes.append(inf)
        return {
            "capitan": self.nombre,
            "fase_tactica": orden_coronel,
            "pelotones_activos": len(self.tenientes),
            "reportes": informes
        }
