"""
Plantilla Base Canónica DEAA-V2.1: Sargento de Escuadra
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .soldado_template import SoldadoBase

class SargentoBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la escuadra")
    escuadra: List[SoldadoBase] = Field(default_factory=list, description="Lista de hasta 5 soldados especialistas")

    def despachar_escuadra(self, orden_teniente: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comanda a su escuadra de soldados atómicos en secuencia controlada."""
        reportes = []
        for soldado in self.escuadra:
            try:
                res = soldado.ejecutar_accion(params or {"orden": orden_teniente})
                reportes.append(res)
            except Exception as e:
                reportes.append({"soldado": soldado.nombre, "error": str(e)})
        return {
            "sargento": self.nombre,
            "orden": orden_teniente,
            "soldados_desplegados": len(self.escuadra),
            "reportes": reportes
        }
