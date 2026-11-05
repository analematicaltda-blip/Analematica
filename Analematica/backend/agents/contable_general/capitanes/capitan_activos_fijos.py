"""
contable_general -> capitanes: capitan_activos_fijos.py
Doctrina Operativa DEAA-V2.1 - Basado en skills-contabilidad/shared/depreciation-schedule
"""
from typing import Dict, Any, List

class CapitanActivosFijos:
    def __init__(self, name: str = "capitan_activos_fijos"):
        self.name = name

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        params = payload or {}

        # Algoritmo de depreciación de activos fijos según NIC 16 / PUC
        activos = [
            {"categoria": "Equipo de Computación y Comunicación", "costo_adquisicion": 180000000.0, "vida_util_meses": 36, "deprec_acumulada": 60000000.0, "deprec_mensual": 5000000.0},
            {"categoria": "Maquinaria y Equipo de Servidores", "costo_adquisicion": 420000000.0, "vida_util_meses": 120, "deprec_acumulada": 70000000.0, "deprec_mensual": 3500000.0},
            {"categoria": "Muebles y Enseres de Oficinas", "costo_adquisicion": 95000000.0, "vida_util_meses": 120, "deprec_acumulada": 15833333.0, "deprec_mensual": 791667.0}
        ]

        total_costo = sum(a["costo_adquisicion"] for a in activos)
        total_acumulada = sum(a["deprec_acumulada"] for a in activos)
        total_mensual = sum(a["deprec_mensual"] for a in activos)
        valor_en_libros = round(total_costo - total_acumulada, 2)

        return {
            "unit": self.name,
            "status": "success",
            "resumen_activos": {
                "total_activos_fijos_cop": total_costo,
                "depreciacion_acumulada_cop": total_acumulada,
                "depreciacion_mensual_cop": total_mensual,
                "valor_neto_en_libros_cop": valor_en_libros,
                "metodo_depreciacion": "LINEA_RECTA_PUC_NIC16"
            },
            "detalle_activos": activos
        }

AgentUnit = CapitanActivosFijos
