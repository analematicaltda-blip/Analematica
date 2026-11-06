from django.test import TestCase
from unittest.mock import MagicMock, patch
from apps.core_erp.event_bus import EventBus
from apps.core_erp.events.erp_events import ErpImpactRequested
import uuid

class CommercialImpactTest(TestCase):
    """
    Test para validar la restauración de la Dimensión 4: Comercial.
    """

    def setUp(self):
        EventBus.clear_subscribers()
        from apps.core_erp.events.impact_subscribers import handle_erp_impact
        EventBus.subscribe("ERP_IMPACT_REQUESTED", handle_erp_impact)

    @patch('django.utils.module_loading.import_string')
    def test_commercial_impact_emitted(self, mock_import_string):
        """
        Valida que al emitir un evento, se cree una Operación Comercial.
        """
        mock_operacion = MagicMock()

        def side_effect(path):
            if 'OperacionComercial' in path: return mock_operacion
            return MagicMock()

        mock_import_string.side_effect = side_effect

        payload = {
            "perfil_id": str(uuid.uuid4()),
            "cliente_id": str(uuid.uuid4()),
            "amount": 500.0
        }
        event = ErpImpactRequested(event_type="SALE", payload=payload)

        EventBus.emit("ERP_IMPACT_REQUESTED", event)

        self.assertTrue(mock_operacion.objects.create.called)
        args, kwargs = mock_operacion.objects.create.call_args
        self.assertEqual(float(kwargs['total']), 500.0)
