from django.test import TestCase
from apps.peace_net.models import SystemicRiskIndicator, StabilityAlert, MitigationScenario
from apps.peace_net.services import StabilityMonitorService
from apps.sarita_agents.orchestrator import sarita_orchestrator
from api.models import CustomUser

class PeaceNetTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username="admin_peace", email="admin@peace.com", password="pass")

    def test_stability_detection_flow(self):
        """Prueba el flujo completo de detección de inestabilidad."""
        # 1. Crear indicadores con tensión
        SystemicRiskIndicator.objects.create(
            name="Tensión de Precios",
            domain="ECONOMIC",
            current_value=150.0,
            baseline_value=100.0,
            threshold_critical=60.0
        )

        # 2. Ejecutar análisis
        alert = StabilityMonitorService.analyze_indicators()

        # 3. Verificar resultados
        self.assertIsNotNone(alert)
        self.assertEqual(alert.severity, StabilityAlert.Severity.MEDIUM)
        self.assertTrue(alert.scenarios.exists())

        scenario = alert.scenarios.first()
        self.assertIn("Alineación Institucional", scenario.title)

    def test_peace_net_agent_mission(self):
        """Prueba la delegación de una misión de estabilidad al Coronel Peace-Net."""
        directive = {
            "domain": "peace_net",
            "objective": "Analizar riesgo sistémico territorial",
            "params": {"region": "META"}
        }

        mision = sarita_orchestrator.start_mission(directive)
        sarita_orchestrator.execute_mission(mision.id)

        mision.refresh_from_db()
        self.assertEqual(mision.estado, 'COMPLETADA')
        self.assertIn("status", mision.resultado_final)
