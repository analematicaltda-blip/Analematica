from django.test import TestCase
from ..governance_kernel import GovernanceKernel

class GovernanceKernelTest(TestCase):
    def test_get_system_health(self):
        health = GovernanceKernel.get_system_health()
        self.assertEqual(health["status"], "OPERATIONAL")
        self.assertIn("uptime", health)
