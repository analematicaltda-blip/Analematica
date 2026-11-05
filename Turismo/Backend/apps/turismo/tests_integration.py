from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider

class TourismIntegrationTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_tourism_provider_creation(self):
        response = self.client.post('/api/v1/mi-negocio/operativa/esp/tourism-providers/', {
            'name': 'Test Provider',
            'provider_type': 'HOTEL',
            'location': 'Test Location'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TourismProvider.objects.count(), 1)

    def test_specialized_modules_routing(self):
        # Check if the specialized module routes are active
        response = self.client.get('/api/v1/mi-negocio/operativa/esp/hoteles/rooms/')
        # Even if empty, it should return 200 OK (list)
        self.assertEqual(response.status_code, 200)
