from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider, TourismService, Reservation
from apps.tourism_intelligence.models import TourismSeasonality
from apps.tourism_intelligence.services import DynamicPricingService
from decimal import Decimal

class IntelligenceIntegrationTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='intel_user', email='intel@test.com', password='password')
        self.client.force_authenticate(user=self.user)

        self.provider_user = CustomUser.objects.create_user(username='p_user', email='p@test.com', password='password')
        self.provider = TourismProvider.objects.create(
            name="Intel Hotel",
            provider_type="HOTEL",
            owner=self.provider_user,
            location="Puerto Gaitán"
        )
        self.service = TourismService.objects.create(
            provider=self.provider,
            service_type="ACCOMMODATION",
            name="Intel Room",
            description="Room for testing",
            price=100.00
        )
        # Setup seasonality for high demand
        TourismSeasonality.objects.create(
            destino="Puerto Gaitán",
            mes=3,
            nivel_demanda="HIGH"
        )

    def test_dynamic_pricing_high_season(self):
        # Service ID is used for suggested price
        suggestion = DynamicPricingService.get_suggested_price(self.service.id)
        self.assertEqual(suggestion['suggested_price'], Decimal('120.00')) # 100 * 1.20
        self.assertEqual(suggestion['adjustment_reason'], "Alta Demanda Estacional")

    def test_forecast_api(self):
        response = self.client.get('/api/v1/tourism/intelligence/intelligence/forecast/', {
            'destino': 'Puerto Gaitán',
            'categoria': 'ACCOMMODATION'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('demanda_estimada', response.data)
