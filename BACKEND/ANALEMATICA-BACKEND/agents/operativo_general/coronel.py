"""
División operativo_general: coronel.py
Doctrina Operativa DEAA-V2.1
"""
from typing import Dict, Any, List
from Analematica.backend.agents.templates.coronel_template import CoronelBase
from Analematica.backend.agents.templates.capitan_template import CapitánBase
from Analematica.backend.agents.templates.teniente_template import TenienteBase
from Analematica.backend.agents.templates.sargento_template import SargentoBase
from Analematica.backend.agents.templates.soldado_template import SoldadoBase

class CoronelOperativo(CoronelBase):
    def __init__(self, **data):
        if "nombre" not in data:
            data["nombre"] = "Coronel Operativo General"
        if "capitanes" not in data:
            cap_turnos = CapitánBase(
                nombre="Capitán de Gestión de Turnos y Personal",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Disponibilidad y Logística",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de Cuadrantes Operativos",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Horas Hombre", especialidad="Cálculo y distribución de jornada laboral"),
                                    SoldadoBase(nombre="Soldado Relevos", especialidad="Programación de turnos y guardias")
                                ]
                            )
                        ]
                    )
                ]
            )
            cap_sla = CapitánBase(
                nombre="Capitán de Acuerdos de Nivel de Servicio (SLA)",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Supervisión de Infraestructura",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de Métricas de Disponibilidad",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Uptime de Servicios", especialidad="Medición de disponibilidad continua"),
                                    SoldadoBase(nombre="Soldado Respuesta a Incidentes", especialidad="Control de tiempos de resolución MTTR")
                                ]
                            )
                        ]
                    )
                ]
            )
            cap_sst = CapitánBase(
                nombre="Capitán de Matriz de Riesgos y SG-SST",
                tenientes=[
                    TenienteBase(
                        nombre="Teniente de Seguridad en Campo",
                        sargentos=[
                            SargentoBase(
                                nombre="Sargento de Inspecciones COPASST",
                                escuadra=[
                                    SoldadoBase(nombre="Soldado Sellado de Actas", especialidad="Validación de matrices y actas COPASST"),
                                    SoldadoBase(nombre="Soldado Aforos y Mitigación", especialidad="Control de capacidad máxima y señalización")
                                ]
                            )
                        ]
                    )
                ]
            )
            data["capitanes"] = [cap_turnos, cap_sla, cap_sst]
        super().__init__(**data)

    def ejecutar_orden_general(self, orden_general: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        base_report = super().ejecutar_orden_general(orden_general, params)
        telemetria = {
            "sla_cumplimiento": 99.8,
            "turnos_activos": 24,
            "incidentes_abiertos": 0,
            "capacidad_aforo_pct": 82.5,
            "insignia": "SLA 99.8% CUMPLIDO",
            "personal_en_turno": 48
        }
        return {
            "status": "success",
            "division": "OPERATIVO",
            "mision": orden_general,
            "telemetria": telemetria,
            "detalle_militar": base_report
        }

AgentUnit = CoronelOperativo
