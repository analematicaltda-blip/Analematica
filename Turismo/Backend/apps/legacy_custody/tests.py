from django.test import TestCase
from api.models import CustomUser
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, AuthorityLevel

class LegacyProtectionTest(TestCase):
    def setUp(self):
        self.super_admin = CustomUser.objects.create_superuser(
            username='sovereign_custodian',
            email='custodian@sarita.gov',
            password='password123',
            role=CustomUser.Role.ADMIN
        )
        self.regular_admin = CustomUser.objects.create_user(
            username='regular_admin',
            email='admin@sarita.gov',
            password='password123',
            role=CustomUser.Role.ADMIN
        )

    def test_prohibit_privatization(self):
        """Verifica que nadie pueda privatizar el sistema (Prohibición de Propiedad Absoluta)."""
        kernel = GovernanceKernel(self.super_admin)
        with self.assertRaises(PermissionError) as cm:
            kernel.resolve_and_execute('PLATFORM_TRANSFER_OWNERSHIP', {})
        self.assertIn("SARITA no puede ser privatizada", str(cm.exception))

    def test_prohibit_auto_modification_by_non_sovereign(self):
        """Verifica que solo la autoridad soberana (SuperUser) pueda evolucionar el núcleo."""
        kernel = GovernanceKernel(self.regular_admin)
        with self.assertRaises(PermissionError) as cm:
            kernel.resolve_and_execute('SYSTEM_EVOLUTION_HARDENING', {})
        self.assertIn("La evolución del núcleo de gobernanza está bloqueada", str(cm.exception))

    def test_unaudited_surveillance_block(self):
        """Verifica que se bloquee la vigilancia sin referencia de auditoría."""
        # Registrar intención de vigilancia para el test
        from apps.admin_plataforma.services.governance_kernel import GovernanceIntention
        GovernanceKernel.register_intention(GovernanceIntention(
            name="ACTIVATE_TRAFFIC_MONITOR",
            domain="surveillance",
            required_role=CustomUser.Role.ADMIN
        ))

        kernel = GovernanceKernel(self.super_admin)
        with self.assertRaises(PermissionError) as cm:
            kernel.resolve_and_execute('ACTIVATE_TRAFFIC_MONITOR', {"scope": "city"})
        self.assertIn("Prohibido cualquier uso de vigilancia que no posea una referencia de auditoría", str(cm.exception))

    def test_legacy_bundle_generation(self):
        """Verifica la generación del paquete de transmisión de conocimiento."""
        from apps.legacy_custody.services import LegacyCustodyService
        service = LegacyCustodyService(self.super_admin)
        bundle = service.generate_legacy_bundle()

        self.assertEqual(bundle["protection_status"], "LOCKED_FOR_CIVILIZATION")
        self.assertIn("principles", bundle["system_standard"])
        self.assertEqual(bundle["system_standard"]["status"], "LEGADO_PROTEGIDO")
