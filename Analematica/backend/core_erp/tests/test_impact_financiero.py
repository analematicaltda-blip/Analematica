from django.test import TestCase
from unittest.mock import MagicMock, patch
from apps.core_erp.event_bus import EventBus
from apps.core_erp.events.erp_events import ErpImpactRequested
import uuid

class FinancialImpactTest(TestCase):
    """
    Test para validar la restauración de la Dimensión 2: Financiera.
    """

    def setUp(self):
        EventBus.clear_subscribers()
        from apps.core_erp.events.impact_subscribers import handle_erp_impact
        EventBus.subscribe("ERP_IMPACT_REQUESTED", handle_erp_impact)

    @patch('django.utils.module_loading.import_string')
    def test_financial_impact_emitted(self, mock_import_string):
        """
        Valida que al emitir un evento de LIQUIDATION, se cree una Orden de Pago.
        """
        mock_orden = MagicMock()

        def side_effect(path):
            if 'OrdenPago' in path: return mock_orden
            return MagicMock()

        mock_import_string.side_effect = side_effect

        payload = {
            "perfil_id": str(uuid.uuid4()),
            "amount": 100.0
        }
        event = ErpImpactRequested(event_type="LIQUIDATION", payload=payload)

        EventBus.emit("ERP_IMPACT_REQUESTED", event)

        self.assertTrue(mock_orden.objects.create.called)
        args, kwargs = mock_orden.objects.create.call_args
        self.assertEqual(kwargs['amount'], 100.0)
