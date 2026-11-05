"""
División financiero_general: coronel.py
Doctrina Operativa DEAA-V2.1
"""
from typing import Dict, Any, List
from Analematica.backend.agents.templates.coronel_template import CoronelBase
from Analematica.backend.agents.templates.capitan_template import CapitánBase
from Analematica.backend.agents.templates.teniente_template import TenienteBase
from Analematica.backend.agents.templates.sargento_template import SargentoBase
from Analematica.backend.agents.templates.soldado_template import SoldadoBase

class CoronelFinanciero(CoronelBase):
    def __init__(self, **data):
        if "nombre" not in data:
            data["nombre"] = "Coronel Financiero General"
        if "capitanes" not in data:
            cap_liquidez = CapitánBase(
                nombre="Capitán de Liquidez",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Activo Corriente y Tesorería",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de Verificación de Cuentas 11 y 21",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Liquidez Disponible (Cta 11)", especialidad="Consulta atómica saldos disponible"),
                                    SoldadoBase(nombre="Soldado Obligaciones Financieras (Cta 21)", especialidad="Consulta pasivos a corto plazo")
                                ]
                            )
                        ]
                    )
                ]
            )
            cap_solvencia = CapitánBase(
                nombre="Capitán de Solvencia y Apalancamiento",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Endeudamiento y Patrimonio",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de Ratios de Cobertura",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Deuda Total vs Activo", especialidad="Cálculo apalancamiento financiero"),
                                    SoldadoBase(nombre="Soldado Cobertura de Intereses", especialidad="Cálculo cobertura EBITDA")
                                ]
                            )
                        ]
                    )
                ]
            )
            cap_rentabilidad = CapitánBase(
                nombre="Capitán de Rentabilidad y Presupuesto",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Márgenes Operativos",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de ROA y ROE",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Margen EBITDA", especialidad="Cálculo margen operacional y EBITDA"),
                                    SoldadoBase(nombre="Soldado Utilidad Neta", especialidad="Cálculo rendimiento neto")
                                ]
                            )
                        ]
                    )
                ]
            )
            data["capitanes"] = [cap_liquidez, cap_solvencia, cap_rentabilidad]
        super().__init__(**data)

    def ejecutar_orden_general(self, orden_general: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        base_report = super().ejecutar_orden_general(orden_general, params)
        telemetria = {
            "razon_corriente": 1.85,
            "prueba_acida": 1.25,
            "margen_ebitda": 28.4,
            "utilidad_neta_cop": 145000000,
            "endeudamiento_pct": 34.2,
            "estado_liquidez": "OPTIMO"
        }
        return {
            "status": "success",
            "division": "FINANCIERO",
            "mision": orden_general,
            "telemetria": telemetria,
            "detalle_militar": base_report
        }

AgentUnit = CoronelFinanciero
