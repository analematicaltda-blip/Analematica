from django.test import TestCase
from django.contrib.auth import get_user_model
from legacy_custody.models import LegacyCustodian, LegacyMilestone, LegacyGuardrail
from legacy_custody.services.bundle_service import BundleService

User = get_user_model()

class LegacyCustodyTests(TestCase):
    def test_create_custodian(self):
        user = User.objects.create_user(username="testcustodian", password="password")
        custodian = LegacyCustodian.objects.create(user=user)
        self.assertEqual(custodian.user.username, "testcustodian")
        self.assertTrue(custodian.is_active)

    def test_bundle_generation(self):
        data = {"event": "SARITA_PEACE_ACCORD", "impact": "GLOBAL"}
        milestone = BundleService.generate_evidence_bundle(
            title="Sello de Paz Sistémica",
            description="Acuerdo de neutralidad algorítmica ratificado.",
            data=data
        )
        self.assertIsNotNone(milestone.integrity_hash)
        self.assertIn("bundle_", milestone.evidence_bundle_path)
        self.assertEqual(milestone.title, "Sello de Paz Sistémica")

    def test_guardrail_creation(self):
        guardrail = LegacyGuardrail.objects.create(
            name="ANTI_PRIVATIZATION",
            description="El sistema no puede ser vendido."
        )
        self.assertEqual(guardrail.name, "ANTI_PRIVATIZATION")
        self.assertTrue(guardrail.is_active)
