from django.test import TestCase
from apps.decision_intelligence.services.strategic_analysis import StrategicAnalysisService
from apps.decision_intelligence.models import StrategyProposal

class StrategicAnalysisTest(TestCase):
    def test_run_audit(self):
        service = StrategicAnalysisService()
        proposals = service.run_full_audit()
        # Verificamos que se generen las 6 propuestas (una por agente)
        self.assertEqual(len(proposals), 6)

        # Verificamos que las propuestas tengan niveles de decisión asignados
        for p in proposals:
            self.assertIn(p.decision_level, [1, 2, 3])
            self.assertIsNotNone(p.accion_sugerida)
