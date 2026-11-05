from django.test import TestCase
from apps.operational_treaties.models import OperationalTreaty, TreatyComplianceAudit, SovereignKillSwitch
from apps.operational_treaties.services import TreatyValidatorService
from apps.admin_plataforma.models import GovernancePolicy
from api.models import CustomUser

class OperationalTreatiesTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username="admin_treaty", email="admin@treaty.com", password="pass")
        self.tit = OperationalTreaty.objects.create(
            name="Test TIT",
            type='TIT',
            guardrails_config={},
            participating_nodes=["NODE_A", "NODE_B"]
        )

    def test_technical_interop_validation(self):
        """Prueba la validación del TIT."""
        valid_payload = {"explanation": "Justificación XAI", "data": "test"}
        invalid_payload = {"data": "test"}

        self.assertTrue(TreatyValidatorService.validate_technical_interop(valid_payload, "NODE_A"))
        self.assertFalse(TreatyValidatorService.validate_technical_interop(invalid_payload, "NODE_A"))
        self.assertFalse(TreatyValidatorService.validate_technical_interop(valid_payload, "NODE_UNKNOWN"))

    def test_neutrality_enforcement(self):
        """Prueba la detección de sesgos geopolíticos (TNA)."""
        tna = OperationalTreaty.objects.create(
            name="Test TNA",
            type='TNA',
            guardrails_config={"prohibited_terms": ["PAIS_X", "IDEOLOGIA_Y"]}
        )

        neutral_proposal = {"title": "Mejorar estabilidad", "description": "Optimizar recursos"}
        biased_proposal = {"title": "Priorizar PAIS_X", "description": "Garantizar hegemonía"}

        self.assertTrue(TreatyValidatorService.enforce_neutrality(neutral_proposal))
        self.assertFalse(TreatyValidatorService.enforce_neutrality(biased_proposal))

    def test_kill_switch(self):
        """Prueba el botón de desconexión institucional."""
        ks, created = SovereignKillSwitch.objects.get_or_create(treaty=self.tit)
        ks.trigger(self.admin, "Prueba de emergencia")

        self.tit.refresh_from_db()
        self.assertFalse(self.tit.is_active)
        self.assertTrue(ks.is_triggered)
