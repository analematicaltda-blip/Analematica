"""
Plantilla Base Canónica DEAA-V2.1: Teniente de Pelotón
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .sargento_template import SargentoBase

class TenienteBase(BaseModel):
    nombre: str = Field(..., description="Nombre del pelotón")
    sargentos: List[SargentoBase] = Field(default_factory=list, description="Lista de sargentos coordinados")

    def coordinar_peloton(self, orden_capitan: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordina y supervisa la ejecución secuencial de sus sargentos de escuadra."""
        resultados = []
        for sargento in self.sargentos:
            res = sargento.despachar_escuadra(orden_capitan, params)
            resultados.append(res)
        return {
            "teniente": self.nombre,
            "mision": orden_capitan,
            "escuadras_ejecutadas": len(self.sargentos),
            "informes": resultados
        }
