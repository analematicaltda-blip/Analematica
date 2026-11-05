from django.test import TestCase
from unittest.mock import MagicMock, patch
from apps.core_erp.event_bus import EventBus
from apps.core_erp.events.erp_events import ErpImpactRequested
import uuid

class AccountingImpactTest(TestCase):
    """
    Test para validar la restauración de la Dimensión 1: Contable.
    """

    def setUp(self):
        # Limpiar suscriptores para evitar contaminación entre tests
        EventBus.clear_subscribers()
        # Registrar el handler manualmente si no se cargó por señales
        from apps.core_erp.events.impact_subscribers import handle_erp_impact
        EventBus.subscribe("ERP_IMPACT_REQUESTED", handle_erp_impact)

    @patch('django.utils.module_loading.import_string')
    def test_accounting_impact_emitted(self, mock_import_string):
        """
        Valida que al emitir un evento, el suscriptor contable intente crear un asiento.
        """
        # Configurar mocks para modelos dinámicos
        mock_asiento = MagicMock()
        mock_periodo = MagicMock()

        # Mapeo de rutas a mocks
        def side_effect(path):
            if 'AsientoContable' in path: return mock_asiento
            if 'PeriodoContable' in path: return mock_periodo
            return MagicMock()

        mock_import_string.side_effect = side_effect

        # Simular que existe un periodo abierto
        mock_periodo.objects.filter.return_value.first.return_value = MagicMock(cerrado=False)

        # Emitir evento
        payload = {
            "perfil_id": str(uuid.uuid4()),
            "description": "Test de impacto contable"
        }
        event = ErpImpactRequested(event_type="SALE", payload=payload)

        EventBus.emit("ERP_IMPACT_REQUESTED", event)

        # Verificar que se intentó crear el asiento
        self.assertTrue(mock_asiento.objects.create.called)
        args, kwargs = mock_asiento.objects.create.call_args
        self.assertEqual(kwargs['provider_id'], payload['perfil_id'])
        self.assertIn("Impacto Automático F1", kwargs['description'])
