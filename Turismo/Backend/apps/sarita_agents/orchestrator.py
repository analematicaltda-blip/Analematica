# backend/apps/sarita_agents/orchestrator.py

import logging
from django.utils import timezone
from apps.application_services.governance_service import GovernanceService
from .agents.general.sarita.coroneles.prestadores.coronel import PrestadoresCoronel
from .agents.general.sarita.coroneles.operativo_general.coronel import CoronelOperativoGeneral
from .agents.general.sarita.coroneles.operativa_turistica.coronel import CoronelOperativaTuristica
from .agents.general.sarita.coroneles.administrador_general.coronel import AdministradorGeneralCoronel
from .agents.general.sarita.coroneles.contable.coronel import CoronelContable
from .agents.general.sarita.coroneles.financiero.coronel import CoronelFinanciero
from .marketing.coronel_marketing import CoronelMarketing
from .finanzas.coronel_finanzas import CoronelFinanzas
from .agents.general.sarita.coroneles.sg_sst.coronel import CoronelSST
from .agents.general.sarita.coroneles.nomina.coronel import CoronelNomina
from apps.peace_net.coronel import PeaceNetCoronel
from apps.wallet.agents.coronel import CoronelMonedero
from apps.delivery.agents.coronel import CoronelDelivery
from .agents.interop.coronel import CoronelInteroperabilidad
from .agents.general.sarita.coroneles.clientes_turistas.coronel import ClientesTuristasCoronel
from .agents.general.sarita.coroneles.gubernamental.coronel import GubernamentalCoronel

logger = logging.getLogger(__name__)

class SaritaOrchestrator:
    """
    El General SARITA.
    Punto de entrada único para todas las directivas.
    Interpreta la intención y delega la misión al Coronel apropiado.
    """

    def __init__(self):
        # El roster de Coroneles bajo el mando del General.
        op_turistica = CoronelOperativaTuristica(general=self)
        self.coroneles = {
            "prestadores": PrestadoresCoronel(general=self),
            "operativo_general": CoronelOperativoGeneral(general=self),
            "operativa_turistica": op_turistica,
            # Retrocompatibilidad de dominios especializados
            "operativo_hospedaje": op_turistica,
            "operativo_gastronomia": op_turistica,
            "operativo_transporte": op_turistica,
            "operativo_nocturno": op_turistica,
            "operativo_guias": op_turistica,
            "operativo_agencia": op_turistica,

            "administrador_general": AdministradorGeneralCoronel(general=self),
            "contabilidad": CoronelContable(general=self),
            "finanzas": CoronelFinanciero(general=self),
            "marketing": CoronelMarketing(general=self, domain="marketing"),
            "finanzas_marketing": CoronelFinanzas(general=self, domain="finanzas_marketing"),
            "sg_sst": CoronelSST(general=self, domain="sg_sst"),
            "nomina": CoronelNomina(general=self, domain="nomina"),
            "peace_net": PeaceNetCoronel(general=self, domain="peace_net"),
            "wallet": CoronelMonedero(general=self),
            "delivery": CoronelDelivery(general=self),
            "interop": CoronelInteroperabilidad(general=self),
            "clientes_turistas": ClientesTuristasCoronel(general=self),
            "gubernamental": GubernamentalCoronel(general=self),
        }
 
        logger.info("GENERAL SARITA: Orquestador inicializado. Coroneles listos para recibir órdenes.")

    def start_mission(self, directive: dict, idempotency_key=None):
        return GovernanceService.create_mission(directive, idempotency_key)

    def execute_mission(self, mision_id: str):
        if GovernanceService.is_autonomy_suspended():
            logger.error(f"S-0: Misión {mision_id} RECHAZADA. Autonomía suspendida por estado de defensa.")
            return

        try:
            mision = GovernanceService.get_mission(mision_id)
        except Exception:
            logger.error(f"CRITICAL: Misión con ID {mision_id} no encontrada para ejecutar.")
            return

        if not self._validate_mission_integrity(mision):
            GovernanceService.update_mission_status(
                mision_id, 'FALLIDA',
                {"error": "Fallo de integridad en la directiva de la misión."}
            )
            return

        logger.info(f"GENERAL SARITA: Ejecutando misión {mision.id}")
        GovernanceService.update_mission_status(mision_id, 'EN_PROGRESO')

        domain = mision.dominio
        coronel = self.coroneles.get(domain)

        if not coronel:
            GovernanceService.update_mission_status(
                mision_id, 'FALLIDA',
                {"error": f"No se encontró un Coronel para el dominio '{domain}'."}
            )
            logger.error(f"Misión {mision.id} falló: No se encontró Coronel para el dominio '{domain}'.")
            return

        logger.info(f"GENERAL SARITA: Delegando misión {mision.id} al Coronel de '{domain}'.")
        coronel.handle_mission(mision)

    def handle_directive(self, directive: dict):
        # EOS Activation: Zero-Touch Onboarding specialized handling
        if directive.get("action") == "ZERO_TOUCH_ONBOARDING":
            return self._orchestrate_onboarding(directive)

        mision = self.start_mission(directive)
        self.execute_mission(mision.id)
        # We fetch the mission again via service to get the final state
        updated_mision = GovernanceService.get_mission(str(mision.id))
        return updated_mision.resultado_final or {"status": "EN_COLA", "mision_id": str(mision.id)}

    def _orchestrate_onboarding(self, directive: dict):
        """
        EOS Core Flow: Lead Qualified -> Automated Provisioning.
        100% Orchestrated, no manual steps.
        Flow: Lead -> Subscription -> Tenant -> Plan -> Budget -> Ledger -> Monitoring.
        """
        from apps.core_erp.event_bus import EventBus
        company_name = directive.get('company_name')
        logger.warning(f"GENERAL SARITA: Initiating Zero-Touch Onboarding for {company_name}")

        try:
            # 1. Confirm Subscription (Commercial Domain)
            sub_res = self.handle_directive({
                "domain": "comercial",
                "action": "ERP_CONFIRM_SALE",
                "parameters": directive
            })

            # 2. Provision Tenant (Core ERP Domain)
            tenant_res = self.handle_directive({
                "domain": "prestadores",
                "action": "ONBOARDING_PRESTADOR",
                "parameters": directive
            })
            tenant_id = tenant_res.get("tenant_id")

            # 3. Apply Plan & Templates (Infrastructure)
            EventBus.emit("TENANT_PROVISIONED", {
                "tenant_id": tenant_id,
                "plan_code": directive.get("plan_code"),
                "initialize_ledger": True,
                "activate_monitoring": True
            })

            # 4. Initialize Budget & First Snapshot
            self.handle_directive({
                "domain": "contable",
                "action": "ERP_GENERATE_BALANCE", # Force initial snapshot
                "parameters": {"tenant_id": tenant_id, "initial": True}
            })

            return {
                "status": "SUCCESS",
                "onboarding_phase": "COMPLETED",
                "tenant_id": tenant_id,
                "message": f"EOS Activated for {company_name}. Monitoring live."
            }
        except Exception as e:
            logger.error(f"EOS ONBOARDING CRITICAL FAILURE: {e}")
            return {"status": "FAILED", "error": str(e)}

    def _validate_mission_integrity(self, mision) -> bool:
        if mision.dominio != mision.directiva_original.get("domain"):
            logger.error(f"S-0: Violación de integridad detectada en misión {mision.id}.")
            return False
        return True

    def _report_error(self, message: str):
        logger.error(f"GENERAL SARITA: Error en la directiva -> {message}")
        return {
            "status": "REJECTED",
            "message": message,
            "report_from": "General SARITA"
        }

sarita_orchestrator = SaritaOrchestrator()
