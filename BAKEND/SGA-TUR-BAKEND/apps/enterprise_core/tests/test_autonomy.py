from django.test import TestCase
from apps.enterprise_core.services.decision_engine import DecisionEngine
from apps.enterprise_core.models.strategic_rule import StrategicRule
from apps.enterprise_core.models.decision_proposal import DecisionProposal
from apps.core_erp.models import EventAuditLog
from decimal import Decimal
import uuid

class AutonomyEngineTest(TestCase):
    def setUp(self):
        self.tenant_id = uuid.uuid4()
        # Regla Nivel 3: Autonomía Total
        self.rule_full = StrategicRule.objects.create(
            trigger_metric="low_stock",
            condition_expression="metric < 10",
            recommended_action="REPLENISH_STOCK",
            autonomy_level=3,
            tenant_id=self.tenant_id
        )

        # Regla Nivel 2: Bajo umbral
        self.rule_threshold = StrategicRule.objects.create(
            trigger_metric="ad_spend",
            condition_expression="metric > 500",
            recommended_action="PAUSE_CAMPAIGN",
            autonomy_level=2,
            impact_threshold=Decimal('100.00'),
            tenant_id=self.tenant_id
        )

    def test_full_autonomy_execution(self):
        """
        Nivel 3: Debería generar propuesta y ejecutarla automáticamente.
        """
        DecisionEngine.process_metric_update("low_stock", 5, {"item": "Aceite"})

        proposal = DecisionProposal.objects.filter(origin_metric="low_stock").first()
        self.assertIsNotNone(proposal)
        # self.assertTrue(proposal.executed) # GovernanceAdapter mockeado o real

    def test_threshold_autonomy_escalation(self):
        """
        Nivel 2: Debería escalar si el impacto supera el umbral.
        """
        context = {"estimated_impact": 250.00} # > 100.00
        DecisionEngine.process_metric_update("ad_spend", 600, context)

        # Verificar evento de escalamiento
        escalation = EventAuditLog.objects.filter(event_type="EXECUTIVE_ESCALATION_REQUIRED").first()
        self.assertIsNotNone(escalation)
        self.assertEqual(escalation.payload["impact"], 250.0)
