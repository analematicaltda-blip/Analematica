from django.test import TestCase
from apps.core_erp.taxation.tax_engine import TaxEngine
from apps.core_erp.intelligence.engines.predictive import PredictiveEngine

class GlobalIntelligenceTest(TestCase):
    def test_tax_engine_initialization(self):
        engine = TaxEngine()
        self.assertIsNotNone(engine)

    def test_predictive_engine_initialization(self):
        engine = PredictiveEngine()
        self.assertIsNotNone(engine)
