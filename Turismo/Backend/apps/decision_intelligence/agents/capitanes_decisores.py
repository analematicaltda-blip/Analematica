import abc
import logging
from typing import Dict, Any
from ..models import StrategyProposal

logger = logging.getLogger(__name__)

class CapitanDecisorBase(abc.ABC):
    """
    Base para todos los Agentes Decisores de SARITA.
    Analizan datos y proponen acciones estratégicas.
    Evolución Fase 6: Ahora incorporan feedback histórico.
    """
    domain = None

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        from apps.ecosystem_optimization.services.performance_tracker import PerformanceTracker
        self.tracker = PerformanceTracker()

    @abc.abstractmethod
    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        """
        Analiza un set de datos y genera una Propuesta Estratégica.
        """
        pass

    def _create_proposal(self, **kwargs) -> StrategyProposal:
        """Helper para persistir la propuesta con refinamiento evolutivo."""

        # Evolución Fase 6: Si la confianza es muy alta, promocionamos automáticamente el nivel de decisión
        trust = self.tracker.get_super_admin_trust_index(self.domain)
        decision_level = kwargs.get('decision_level', StrategyProposal.DecisionLevel.LEVEL_3)

        if trust > 0.95 and decision_level == StrategyProposal.DecisionLevel.LEVEL_2:
            logger.info(f"EVOLUCIÓN: Promocionando propuesta de {self.domain} a Nivel 1 por alta confianza.")
            kwargs['decision_level'] = StrategyProposal.DecisionLevel.LEVEL_1

        return StrategyProposal.objects.create(
            domain=self.domain,
            agent_id=self.agent_id,
            **kwargs
        )

class CapitanDecisorFinanciero(CapitanDecisorBase):
    domain = StrategyProposal.Domain.FINANCIERO

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE FINANCIERO ({self.agent_id}): Analizando salud económica...")

        # Heurística de Riesgo: Si el unpaid_dues > 1000 y cash_flow bajo
        unpaid = data.get("unpaid_dues", 0)

        return self._create_proposal(
            contexto_detectado=f"Detectada deuda pendiente de ${unpaid}. Riesgo de liquidez moderado.",
            riesgo_actual="Afectación del flujo de caja operativo para el próximo trimestre.",
            oportunidad_detectada="Optimización de cobranza automatizada.",
            accion_sugerida={
                "intention": "ERP_VIEW_CASH_FLOW",
                "parameters": {"mode": "recovery", "target": "high_debt"}
            },
            impacto_estimado="Recuperación proyectada del 30% de cartera vencida.",
            nivel_confianza=0.85,
            nivel_urgencia=StrategyProposal.UrgencyLevel.HIGH,
            nivel_riesgo=StrategyProposal.RiskLevel.MEDIUM,
            decision_level=StrategyProposal.DecisionLevel.LEVEL_2
        )

class CapitanDecisorOperativo(CapitanDecisorBase):
    domain = StrategyProposal.Domain.OPERATIVO

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE OPERATIVO ({self.agent_id}): Analizando desempeño...")

        error_rate = data.get("error_rate_1h", 0)

        if error_rate > 10:
             return self._create_proposal(
                contexto_detectado=f"Pico de errores detectado ({error_rate} errores/hora).",
                riesgo_actual="Inestabilidad de servicios críticos para prestadores.",
                oportunidad_detectada="Autoreparación de servicios y limpieza de caché.",
                accion_sugerida={
                    "intention": "ERP_MANAGE_RESOURCES",
                    "parameters": {"action": "restart_subsystem", "target": "auth"}
                },
                impacto_estimado="Estabilización del 100% de la tasa de error.",
                nivel_confianza=0.95,
                nivel_urgencia=StrategyProposal.UrgencyLevel.CRITICAL,
                nivel_riesgo=StrategyProposal.RiskLevel.LOW,
                decision_level=StrategyProposal.DecisionLevel.LEVEL_1 # Automática
            )

        return self._create_proposal(
            contexto_detectado="Carga del sistema nominal.",
            riesgo_actual="N/A",
            oportunidad_detectada="Mantenimiento preventivo de rutina.",
            accion_sugerida={
                "intention": "ERP_MANAGE_RESOURCES",
                "parameters": {"action": "cleanup_logs"}
            },
            impacto_estimado="Liberación de espacio en disco.",
            nivel_confianza=0.99,
            nivel_urgencia=StrategyProposal.UrgencyLevel.LOW,
            nivel_riesgo=StrategyProposal.RiskLevel.LOW,
            decision_level=StrategyProposal.DecisionLevel.LEVEL_1
        )

class CapitanDecisorComercial(CapitanDecisorBase):
    domain = StrategyProposal.Domain.COMERCIAL

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE COMERCIAL ({self.agent_id}): Analizando funnel de ventas...")
        return self._create_proposal(
            contexto_detectado="Alta tasa de rebote en la página de checkout detectada.",
            riesgo_actual="Pérdida de conversiones potenciales del 40% durante la última semana.",
            oportunidad_detectada="Simplificación del formulario de pago y habilitación de nuevos métodos.",
            accion_sugerida={
                "intention": "PLATFORM_UPDATE_WEB_CMS",
                "parameters": {"layout": "simplified_checkout", "enable_express_pay": True}
            },
            impacto_estimado="Incremento proyectado del 10% en conversiones.",
            nivel_confianza=0.78,
            nivel_urgencia=StrategyProposal.UrgencyLevel.HIGH,
            nivel_riesgo=StrategyProposal.RiskLevel.LOW,
            decision_level=StrategyProposal.DecisionLevel.LEVEL_3
        )

class CapitanDecisorNormativo(CapitanDecisorBase):
    domain = StrategyProposal.Domain.NORMATIVO

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE NORMATIVO ({self.agent_id}): Verificando cumplimiento...")
        return self._create_proposal(
            contexto_detectado="Nueva regulación de protección de datos (Ley 1581) requiere actualización de términos.",
            riesgo_actual="Sanciones legales potenciales por incumplimiento de política de privacidad.",
            oportunidad_detectada="Actualización proactiva para generar confianza en los prestadores.",
            accion_sugerida={
                "intention": "PLATFORM_UPDATE_LEGAL",
                "parameters": {"version": "2.1", "enforce_acceptance": True}
            },
            impacto_estimado="Cumplimiento del 100% del marco legal vigente.",
            nivel_confianza=1.0,
            nivel_urgencia=StrategyProposal.UrgencyLevel.CRITICAL,
            nivel_riesgo=StrategyProposal.RiskLevel.HIGH,
            decision_level=StrategyProposal.DecisionLevel.LEVEL_3 # Estratégica
        )

class CapitanDecisorContable(CapitanDecisorBase):
    domain = StrategyProposal.Domain.SISTEMICO # Usamos sistémico para contabilidad global

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE CONTABLE ({self.agent_id}): Auditando balances...")
        pending = data.get("pending_invoices", 0)
        return self._create_proposal(
            contexto_detectado=f"Existen {pending} facturas sistémicas pendientes de conciliación.",
            riesgo_actual="Descuadre en el cierre contable mensual.",
            oportunidad_detectada="Automatización de conciliación bancaria vs ERP.",
            accion_sugerida={
                "intention": "ERP_GENERATE_BALANCE",
                "parameters": {"auto_reconcile": True}
            },
            impacto_estimado="Cierre contable en tiempo récord con 0 errores.",
            nivel_confianza=0.90,
            nivel_urgencia=StrategyProposal.UrgencyLevel.MEDIUM,
            nivel_riesgo=StrategyProposal.RiskLevel.LOW,
            decision_level=StrategyProposal.DecisionLevel.LEVEL_2
        )

class CapitanDecisorArchivistico(CapitanDecisorBase):
    domain = StrategyProposal.Domain.SISTEMICO

    def analyze_and_propose(self, data: Dict[str, Any]) -> StrategyProposal:
        logger.info(f"AGENTE ARCHIVÍSTICO ({self.agent_id}): Revisando integridad documental...")
        storage = data.get("storage_usage", 0)

        level = StrategyProposal.DecisionLevel.LEVEL_2
        if storage > 0.90:
            level = StrategyProposal.DecisionLevel.LEVEL_3 # Crítico, requiere decisión estratégica de expansión

        return self._create_proposal(
            contexto_detectado=f"Uso de almacenamiento al {int(storage*100)}%.",
            riesgo_actual="Pérdida de capacidad de carga de documentos de prestadores.",
            oportunidad_detectada="Migración a almacenamiento en frío para documentos antiguos.",
            accion_sugerida={
                "intention": "ERP_SEARCH_DOCUMENT",
                "parameters": {"action": "archive_old", "threshold_days": 365}
            },
            impacto_estimado="Liberación del 20% de espacio inmediato.",
            nivel_confianza=0.98,
            nivel_urgencia=StrategyProposal.UrgencyLevel.HIGH,
            nivel_riesgo=StrategyProposal.RiskLevel.LOW,
            decision_level=level
        )
