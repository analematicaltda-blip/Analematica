from django.test import TestCase
from api.models import CustomUser
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, AuthorityLevel
from apps.governance_live.models import SystemicState
from apps.governance_live.services import GovernanceMemoryService
from apps.peace_net.models import StabilityAlert

class GovernanceLiveTests(TestCase):
    def setUp(self):
        self.superadmin = CustomUser.objects.create_superuser(
            username='sovereign_admin',
            email='admin@gob.co',
            password='password123'
        )
        self.agent_user = CustomUser.objects.create(
            username='agent_comercial',
            role=CustomUser.Role.ADMIN,
            is_agent=True,
            agent_domain='comercial'
        )

    def test_systemic_state_transition(self):
        """Verifica la transición de estados gobernada por el SuperAdmin."""
        kernel = GovernanceKernel(self.superadmin)
        state = kernel.transition_systemic_state(
            new_level='CONTAINMENT',
            reason='Simulacro de Crisis Nacional'
        )
        self.assertEqual(state.current_level, 'CONTAINMENT')
        self.assertEqual(kernel.get_current_systemic_state(), 'CONTAINMENT')

    def test_state_restriction_enforcement(self):
        """Verifica que el estado de contención bloquee autonomía delegada."""
        # 1. Activar Contención
        kernel_admin = GovernanceKernel(self.superadmin)
        kernel_admin.transition_systemic_state('CONTAINMENT', 'Bloqueo preventivo')

        # 2. Intentar acción como usuario regular
        kernel_agent = GovernanceKernel(self.agent_user)
        with self.assertRaises(PermissionError) as cm:
            kernel_agent.resolve_and_execute("ERP_GENERATE_BALANCE", {})

        self.assertIn("SISTEMA EN MODO CONTAINMENT", str(cm.exception))

    def test_anti_drift_guardrails(self):
        """Verifica que un agente no pueda operar fuera de su dominio."""
        kernel = GovernanceKernel(self.agent_user)

        # Intentar acción en dominio 'hacienda' siendo agente de 'comercial'
        with self.assertRaises(PermissionError) as cm:
            kernel.resolve_and_execute("PUBLIC_BUDGET_OPTIMIZATION", {})

        self.assertIn("DERIVA DETECTADA", str(cm.exception))

    def test_institutional_memory_recording(self):
        """Verifica el registro de eventos en la memoria."""
        alert = StabilityAlert.objects.create(
            severity='HIGH',
            context_summary='Pico de desinformación detectado',
            detected_patterns={'volatility': 0.8}
        )

        memory = GovernanceMemoryService.record_crisis_resolution(
            alert_id=alert.id,
            actions=['DECOUPLING_SOCIAL_SIGNAL'],
            effectiveness=0.9,
            lessons='La desconexión rápida evitó el pánico.'
        )

        self.assertEqual(memory.event_type, 'CRISIS_HIGH')
        self.assertEqual(memory.effectiveness_score, 0.9)
