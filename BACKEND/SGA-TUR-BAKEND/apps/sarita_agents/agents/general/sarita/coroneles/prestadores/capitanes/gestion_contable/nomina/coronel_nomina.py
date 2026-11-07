import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitan_nomina import CapitanNomina
from .capitan_liquidacion_contratos import CapitanLiquidacionContratos
from .capitan_legal_laboral import CapitanLegalLaboral
from .capitan_pagos_y_tesoreria import CapitanPagosYTesoreria
from .capitan_novedades_y_ausencias import CapitanNovedadesYAusencias
from .capitan_datos_maestros_empleados import CapitanDatosMaestrosEmpleados

logger = logging.getLogger(__name__)

class CoronelNomina(CoronelTemplate):
    """
    Coronel de Nómina: Gobierno integral de las relaciones laborales y compensaciones.
    """
    def _get_capitanes(self) -> dict:
        return {
            "nomina_general": CapitanNomina(coronel=self),
            "liquidacion": CapitanLiquidacionContratos(coronel=self),
            "legal_laboral": CapitanLegalLaboral(coronel=self),
            "pagos": CapitanPagosYTesoreria(coronel=self),
            "novedades": CapitanNovedadesYAusencias(coronel=self),
            "empleados": CapitanDatosMaestrosEmpleados(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")
        mapping = {
            "RUN_PAYROLL": "nomina_general",
            "TERMINATE_CONTRACT": "liquidacion",
            "AUDIT_LABOR_LAW": "legal_laboral",
            "PROCESS_PAYROLL_PAYMENT": "pagos",
            "REGISTER_ABSENCE": "novedades",
            "UPDATE_EMPLOYEE": "empleados",
        }
        cap_key = mapping.get(m_type, "nomina_general")
        return self.capitanes.get(cap_key)
