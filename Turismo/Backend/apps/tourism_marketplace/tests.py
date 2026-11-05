from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider, TourismService
from apps.tourism_marketplace.models import ProductRanking, ProviderReputation

class MarketplaceIntegrationTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='market_user', email='market@test.com', password='password')
        self.client.force_authenticate(user=self.user)

        self.provider_user = CustomUser.objects.create_user(username='prov_user', email='prov@test.com', password='password')
        self.provider = TourismProvider.objects.create(
            name="Marketplace Hotel",
            provider_type="HOTEL",
            owner=self.provider_user
        )
        self.service = TourismService.objects.create(
            provider=self.provider,
            service_type="ACCOMMODATION",
            name="Suite Marketplace",
            description="Luxury suite",
            price=150.00
        )
        # Create initial ranking
        self.ranking = ProductRanking.objects.create(service=self.service, score_total=0.95)

    def test_recommendations_api(self):
        response = self.client.get('/api/v1/marketplace/discovery/recommendations/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['name'], "Suite Marketplace")

    def test_review_creation(self):
        response = self.client.post('/api/v1/marketplace/reviews/', {
            'service': str(self.service.id),
            'rating': 5,
            'comment': 'Excelente servicio marketplace'
        })
        self.assertEqual(response.status_code, 201)
