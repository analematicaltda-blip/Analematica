# backend/apps/sarita_agents/agents/general/sarita/coroneles/administrador_general/coronel.py

from .....coronel_template import CoronelTemplate
from .capitanes.capitan_auditoria_global import CapitanAuditoriaGlobal
from .capitanes.operativos.capitan_ventas import AdminCapitanVentas
from .capitanes.operativos.capitan_contabilidad import AdminCapitanContabilidad
from .capitanes.operativos.capitan_financiero import AdminCapitanFinanciero
from .capitanes.operativos.capitan_operativo import AdminCapitanOperativo
from .capitanes.operativos.capitan_archivistico import AdminCapitanArchivistico

class AdministradorGeneralCoronel(CoronelTemplate):
    """
    Coronel para el dominio de Administración General.
    Gestiona auditorías, seguridad, monitoreo y configuración global.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="administrador_general")

    def _get_capitanes(self) -> dict:
        return {
            "auditoria": CapitanAuditoriaGlobal(coronel=self),
            "admin_ventas": AdminCapitanVentas(coronel=self),
            "admin_contabilidad": AdminCapitanContabilidad(coronel=self),
            "admin_financiero": AdminCapitanFinanciero(coronel=self),
            "admin_operativo": AdminCapitanOperativo(coronel=self),
            "admin_archivistico": AdminCapitanArchivistico(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        mission_info = directiva.get("mission", {})
        mission_type = mission_info.get("type")

        # Mapeo de Intenciones a Capitanes
        mapping = {
            "AUDITORIA_GLOBAL": "auditoria",
            "ERP_VIEW_SALES_STATS": "admin_ventas",
            "ADMIN_VENTAS": "admin_ventas",
            "ERP_CREATE_VOUCHER": "admin_contabilidad",
            "ADMIN_CONTABILIDAD": "admin_contabilidad",
            "ERP_VIEW_CASH_FLOW": "admin_financiero",
            "ADMIN_FINANCIERO": "admin_financiero",
            "ERP_MANAGE_RESOURCES": "admin_operativo",
            "ERP_SEARCH_DOCUMENT": "admin_archivistico"
        }

        cap_key = mapping.get(mission_type)
        if cap_key:
            return self.capitanes.get(cap_key)

        return super()._select_capitan(directiva)
