from django.test import TestCase
from unittest.mock import MagicMock, patch
from apps.core_erp.event_bus import EventBus
from apps.core_erp.events.erp_events import ErpImpactRequested
import uuid

class AnalyticalImpactTest(TestCase):
    """
    Test para validar la restauración de la Dimensión 5: Analítica.
    """

    def setUp(self):
        EventBus.clear_subscribers()
        from apps.core_erp.events.impact_subscribers import handle_erp_impact
        EventBus.subscribe("ERP_IMPACT_REQUESTED", handle_erp_impact)

    @patch('django.utils.module_loading.import_string')
    def test_analytical_impact_emitted(self, mock_import_string):
        """
        Valida que al emitir un evento con monto, se registre una métrica SaaS.
        """
        mock_metric = MagicMock()

        def side_effect(path):
            if 'SaaSMetric' in path: return mock_metric
            return MagicMock()

        mock_import_string.side_effect = side_effect

        payload = {
            "amount": 1250.0
        }
        event = ErpImpactRequested(event_type="SALE", payload=payload)

        EventBus.emit("ERP_IMPACT_REQUESTED", event)

        self.assertTrue(mock_metric.objects.create.called)
        args, kwargs = mock_metric.objects.create.call_args
        self.assertEqual(kwargs['metric_name'], "REVENUE_EVENT")
        self.assertEqual(float(kwargs['value']), 1250.0)
