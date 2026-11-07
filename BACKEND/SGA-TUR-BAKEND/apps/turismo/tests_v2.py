from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider
from apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.restaurantes.models import RestaurantTable
from apps.sarita_agents.agents.general.sarita.coroneles.operativa_turistica.directos.tenientes_especializados import TenienteOperativoGastronomia

class TourismFunctionalTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='agent_test', email='agent@sarita.ai', password='password')
        self.provider_user = CustomUser.objects.create_user(username='rest_owner', email='owner@rest.com', password='password')
        self.table = RestaurantTable.objects.create(
            provider_id=self.provider_user.id,
            table_number='101',
            capacity=4
        )

    def test_teniente_gastronomia_real_flow(self):
        teniente = TenienteOperativoGastronomia()
        params = {
            "mesa_id": self.table.id,
            "accion": "PROCESS_COMMAND",
            "user_id": self.user.id,
            "items": [{"id": 1, "name": "Bandeja Paisa"}]
        }

        # El teniente llama al SargentoRestaurante real
        res = teniente.perform_action(params)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["mesa"], "101")

        # Verificar cambio de estado en DB
        self.table.refresh_from_db()
        self.assertEqual(self.table.status, RestaurantTable.TableStatus.OCCUPIED)
