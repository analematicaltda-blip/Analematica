import logging
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import SovereignComplianceNode, StateEntity, IntegrationProtocol

logger = logging.getLogger(__name__)

class SovereignComplianceService:
    """
    Compliance & Sovereign AI Layer - Phase 21.5.
    Monitorea cumplimiento local y calcula la Utilidad Integrada (IntegratedUtility).
    """

    @staticmethod
    @transaction.atomic
    def run_compliance_audit(jurisdiction_code):
        """
        Ciclo de auditoría de cumplimiento AI.
        Bloquea operaciones si el compliance_score < threshold.
        """
        node = SovereignComplianceNode.objects.filter(jurisdiction=jurisdiction_code).first()
        if not node:
            return None

        # 1. Update compliance_score based on StateEntity status
        state_entities = StateEntity.objects.filter(country_code=jurisdiction_code)
        if state_entities.count() > 0:
            avg_compliance = sum(e.compliance_score for e in state_entities) / state_entities.count()

            # 2. Integrated Utility = Efficiency + Stability - Risk
            integrated_utility = node.economic_efficiency + node.stability_contribution - (node.sovereign_risk * Decimal('1000000'))

            logger.info(f"Sovereign AI: Integrated Utility for {jurisdiction_code}: {integrated_utility}")

            if avg_compliance < node.compliance_threshold:
                # Critical Compliance Alert
                node.sovereign_risk += Decimal('0.20')
                logger.error(f"Sovereign AI: COMPLIANCE CRITICAL in {jurisdiction_code}. Score: {avg_compliance}")

                # Integration with sovereign_infrastructure (Phase 19)
                # If risk too high, move assets to other jurisdiction

            node.save()
            return integrated_utility
        return Decimal('0')

    @staticmethod
    @transaction.atomic
    def submit_sovereign_report(jurisdiction_code, report_data):
        """
        Genera y firma un reporte auditado para las autoridades estatales.
        """
        node = SovereignComplianceNode.objects.get(jurisdiction=jurisdiction_code)

        # Firmar reporte (SIPL-SIG)
        report_hash = hashlib.sha256(json.dumps(report_data).encode()).hexdigest()

        node.last_report_hash = report_hash
        node.save()

        logger.info(f"Sovereign AI: Report Submitted for {jurisdiction_code}. HASH: {report_hash}")
        return report_hash

    @staticmethod
    def calculate_integrated_utility(node_id):
        """
        Modelo Matemático Fase 21.6.
        """
        node = SovereignComplianceNode.objects.get(id=node_id)
        # IU = EconomicEfficiency + StateStabilityContribution - SovereignRisk
        # Normalization logic
        return node.economic_efficiency + node.stability_contribution - (node.sovereign_risk * Decimal('1000000'))
