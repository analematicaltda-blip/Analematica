
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from api.models import CustomUser
from apps.comercial.models import Plan, Subscription
from apps.domain_business.operativa.models import ProviderProfile
from django.contrib.contenttypes.models import ContentType

class AdminPlataformaAPITestCase(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Crear un prestador como cliente para las suscripciones
        self.prestador_user = CustomUser.objects.create_user('prestador_cliente', 'cliente@test.com', 'password', role='PRESTADOR')
        self.prestador_profile = ProviderProfile.objects.create(usuario=self.prestador_user, nombre_comercial='Cliente de Prueba')

    def test_admin_can_create_plan(self):
        """Asegura que un admin puede crear un nuevo plan."""
        url = '/api/admin/plataforma/planes/'
        data = {
            'name': 'Plan Básico',
            'code': 'BASIC-01',
            'description': 'Un plan básico para prestadores.',
            'monthly_price': '99.99',
            'target_user_type': 'PROVIDER'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(Plan.objects.get().name, 'Plan Básico')

    def test_admin_can_create_suscripcion(self):
        """Asegura que un admin puede crear una suscripción para un cliente."""
        plan = Plan.objects.create(name='Plan Test', code='TEST-01', monthly_price=100, target_user_type='PROVIDER')

        url = '/api/admin/plataforma/suscripciones/'
        data = {
            'plan_id': plan.pk,
            'cliente_id': str(self.prestador_profile.pk),
            'start_date': timezone.now().date().isoformat(),
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.filter(perfil_ref_id=self.prestador_profile.pk).count(), 1)

    def test_non_admin_cannot_access_planes(self):
        """Asegura que un usuario no-admin no puede acceder a los endpoints de planes."""
        non_admin_client = APIClient()
        non_admin_client.force_authenticate(user=self.prestador_user)

        url = '/api/admin/plataforma/planes/'
        response = non_admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
