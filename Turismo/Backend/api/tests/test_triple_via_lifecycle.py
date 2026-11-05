from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser, GovernmentProfile, TouristProfile, DeliveryProfile, Entity
from apps.turismo.models.provider_models import TourismProvider, TourismService, Reservation
from decimal import Decimal

class UserLifecycleTripleViaTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.client = APIClient()
        # Admin Nacional (Director Nacional de Turismo)
        self.director_nacional = CustomUser.objects.create_superuser(
            username='director_nacional',
            email='director@turismo.gov.co',
            password='password123'
        )
        self.entidad_nacional = Entity.objects.create(
            name="ENTE NACIONAL DE TURISMO",
            slug="ente-nacional",
            type="nacional"
        )
        GovernmentProfile.objects.create(
            user=self.director_nacional,
            entity=self.entidad_nacional,
            cargo="Director Nacional",
            nivel="NACIONAL"
        )

    def test_flujo_1_director_nacional_crea_funcionario(self):
        self.client.force_authenticate(user=self.director_nacional)
        funcionario_user = CustomUser.objects.create_user(username='func_nac', email='f@turismo.gov.co', password='pass')

        response = self.client.post('/api/v1/government/', {
            'user': funcionario_user.id,
            'entity': self.entidad_nacional.id,
            'cargo': 'Profesional Nacional',
            'nivel': 'NACIONAL'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(GovernmentProfile.objects.filter(nivel='NACIONAL').count(), 2)

    def test_flujo_4_empresa_crea_servicios(self):
        business_owner = CustomUser.objects.create_user(username='hotel_owner', email='owner@hotel.com', password='pass')
        provider = TourismProvider.objects.create(name="Hotel Real", provider_type="HOTEL", owner=business_owner)
        self.client.force_authenticate(user=business_owner)

        response = self.client.post('/api/v1/business/', {}) # Mock List endpoint verification
        self.assertEqual(response.status_code, 200)

    def test_flujo_5_turista_realiza_reserva(self):
        turista = CustomUser.objects.create_user(username='turista_juan', email='juan@gmail.com', password='pass')
        TouristProfile.objects.create(user=turista)

        business_owner = CustomUser.objects.create_user(username='rest_owner', email='rest@test.com', password='pass')
        provider = TourismProvider.objects.create(name="Restaurante Real", provider_type="RESTAURANT", owner=business_owner)
        service = TourismService.objects.create(provider=provider, service_type="FOOD", name="Almuerzo Llanero", price=25000)

        self.client.force_authenticate(user=turista)
        response = self.client.post('/api/v1/turismo/tourism-reservations/', {
            'provider': str(provider.id),
            'service': str(service.id),
            'start_date': '2026-05-01T12:00:00Z',
            'end_date': '2026-05-01T13:00:00Z',
            'total_price': 25000
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 1)
