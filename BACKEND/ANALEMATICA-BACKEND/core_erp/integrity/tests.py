# backend/apps/core_erp/integrity/tests.py
from django.test import TestCase
from .system_integrity_certifier import SystemIntegrityCertifier

class SystemIntegrityTest(TestCase):
    def test_full_certification_execution(self):
        """
        Valida que el motor de certificación se ejecute sin errores y genere el reporte.
        """
        certifier = SystemIntegrityCertifier()
        report = certifier.run_full_certification()

        self.assertIn("certification_level", report)
        self.assertIn("integrity_score", report)
        self.assertTrue(len(report["components"]) > 0)

    def test_architecture_isolation(self):
        """
        Valida el validador de arquitectura específicamente.
        """
        from .architecture_validator import ArchitectureValidator
        validator = ArchitectureValidator()
        res = validator.validate()

        self.assertEqual(res["component"], "DomainIsolation")
        self.assertIn("score", res)
