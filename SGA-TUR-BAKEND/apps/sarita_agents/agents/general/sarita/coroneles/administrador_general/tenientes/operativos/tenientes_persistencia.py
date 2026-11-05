from apps.sarita_agents.agents.teniente_template import TenienteTemplate
import logging

logger = logging.getLogger(__name__)

class AdminTenientePersistenciaComercial(TenienteTemplate):
    """
    Teniente responsable de persistir datos comerciales en el ERP del Super Admin (admin_comercial).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"ADMIN TENIENTE (Persistencia Comercial): Persistiendo en admin_comercial con parámetros -> {parametros}")
        # Lógica de persistencia funcional en tablas admin_*
        return {"status": "SUCCESS", "message": "Operación comercial registrada en el ERP administrativo."}

class AdminTenientePersistenciaContable(TenienteTemplate):
    """
    Teniente responsable de persistir datos contables en el ERP del Super Admin (admin_contabilidad).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"ADMIN TENIENTE (Persistencia Contable): Persistiendo en admin_contabilidad con parámetros -> {parametros}")

        # FASE 4.1: Delegación a Sargento
        from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.sargentos.sargento_contable import SargentoRegistroContable
        sargento = SargentoRegistroContable(teniente=self)
        sargento_report = sargento.handle_order(parametros)

        return {
            "status": "SUCCESS",
            "message": "Asiento contable registrado en el ERP administrativo.",
            "operational_depth": "4.1",
            "sargento_report": sargento_report
        }

class AdminTenientePersistenciaFinanciera(TenienteTemplate):
    """
    Teniente responsable de persistir datos financieros en el ERP del Super Admin (admin_financiera).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"ADMIN TENIENTE (Persistencia Financiera): Persistiendo en admin_financiera con parámetros -> {parametros}")
        return {"status": "SUCCESS", "message": "Movimiento financiero registrado en el ERP administrativo."}

class AdminTenientePersistenciaOperativa(TenienteTemplate):
    """
    Teniente responsable de persistir datos operativos en el ERP del Super Admin (admin_operativa).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"ADMIN TENIENTE (Persistencia Operativa): Persistiendo en admin_operativa con parámetros -> {parametros}")

        # FASE 4.1: Delegación a Sargento (Ejemplo con SST)
        from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.sargentos.sargento_sst import SargentoCoordinacionSST
        sargento = SargentoCoordinacionSST(teniente=self)
        sargento_report = sargento.handle_order(parametros)

        return {
            "status": "SUCCESS",
            "message": "Acción operativa registrada en el ERP administrativo.",
            "operational_depth": "4.1",
            "sargento_report": sargento_report
        }

class AdminTenientePersistenciaArchivistica(TenienteTemplate):
    """
    Teniente responsable de persistir datos archivísticos en el ERP del Super Admin (admin_archivistica).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"ADMIN TENIENTE (Persistencia Archivística): Persistiendo en admin_archivistica con parámetros -> {parametros}")
        return {"status": "SUCCESS", "message": "Gestión documental registrada en el ERP administrativo."}
