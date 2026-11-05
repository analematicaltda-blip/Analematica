from django.test import TestCase
from apps.enterprise_core.services.decision_engine import DecisionEngine
from apps.enterprise_core.models.decision_proposal import DecisionProposal
from apps.enterprise_core.models.strategic_rule import StrategicRule
from apps.core_erp.tenancy.models import Tenant
from decimal import Decimal
import uuid

class Phase9IntelligenceTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Phase 9 Test Tenant", tax_id="PH9-001")

        # Create a Level 3 (Autonomous) rule
        self.rule = StrategicRule.objects.create(
            tenant_id=self.tenant.id,
            name="Auto Stock Recovery",
            trigger_metric="inventory_level",
            condition_expression="metric < 10",
            recommended_action="RECOVER_STOCK",
            autonomy_level=3,
            risk_weight=0.2,
            is_active=True
        )

    def test_autonomous_execution_flow(self):
        """
        Tests that a metric update triggers a proposal and Level 3 auto-execution.
        """
        # Simulate metric update
        DecisionEngine.process_metric_update(
            metric_name="inventory_level",
            value=5,
            context={"item_id": "test-item", "estimated_impact": 100}
        )

        # Verify proposal was created and executed
        proposal = DecisionProposal.objects.filter(origin_metric="inventory_level").first()
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.autonomy_level_applied, 3)

        # Note: In test environment, GovernanceAdapter might return failure if kernel not fully setup,
        # but the engine should at least attempt execution and mark as EXECUTED in the model logic
        # if the adapter call succeeds.
        self.assertTrue(proposal.executed)
        self.assertEqual(proposal.governance_status, DecisionProposal.Status.EXECUTED)
