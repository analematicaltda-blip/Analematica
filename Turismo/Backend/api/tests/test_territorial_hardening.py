from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser, Profile, Verificacion, PlantillaVerificacion
from apps.turismo.models.provider_models import TourismProvider
from apps.turismo.models.divipola import Department, Municipality
import uuid

class TerritorialHardeningTest(TestCase):
    databases = {'default'}

    def setUp(self):
        self.client = APIClient()

        # 1. Setup DIVIPOLA
        self.dept_meta = Department.objects.create(code='50', name='Meta')
        self.dept_antioquia = Department.objects.create(code='05', name='Antioquia')

        self.mun_gaitan = Municipality.objects.create(code='50568', name='Puerto Gaitan', dept=self.dept_meta)
        self.mun_villavo = Municipality.objects.create(code='50001', name='Villavicencio', dept=self.dept_meta)
        self.mun_medellin = Municipality.objects.create(code='05001', name='Medellin', dept=self.dept_antioquia)

        # 2. Setup Officials
        self.admin = CustomUser.objects.create_superuser(username='admin', email='admin@test.com', password='p')

        self.func_gaitan = CustomUser.objects.create_user(username='f_gaitan', role='DIRECTIVO_MUNICIPAL')
        Profile.objects.create(user=self.func_gaitan, department=self.dept_meta, municipality=self.mun_gaitan)

        self.func_meta = CustomUser.objects.create_user(username='f_meta', role='DIRECTIVO_DEPARTAMENTAL')
        Profile.objects.create(user=self.func_meta, department=self.dept_meta)

        # 3. Setup Providers
        self.prov_gaitan = TourismProvider.objects.create(
            id=uuid.uuid4(), name="Hotel Gaitan", owner=self.admin,
            department=self.dept_meta, municipality=self.mun_gaitan
        )
        self.prov_villavo = TourismProvider.objects.create(
            id=uuid.uuid4(), name="Hotel Villavo", owner=self.admin,
            department=self.dept_meta, municipality=self.mun_villavo
        )
        self.prov_medellin = TourismProvider.objects.create(
            id=uuid.uuid4(), name="Hotel Medellin", owner=self.admin,
            department=self.dept_antioquia, municipality=self.mun_medellin
        )

        # 4. Setup Verifications
        self.plantilla = PlantillaVerificacion.objects.create(nombre="Test")
        Verificacion.objects.create(plantilla_usada=self.plantilla, prestador_ref_id=self.prov_gaitan.id, fecha_visita='2026-01-01')
        Verificacion.objects.create(plantilla_usada=self.plantilla, prestador_ref_id=self.prov_villavo.id, fecha_visita='2026-01-01')
        Verificacion.objects.create(plantilla_usada=self.plantilla, prestador_ref_id=self.prov_medellin.id, fecha_visita='2026-01-01')

    def test_municipal_isolation(self):
        """Funcionario de Gaitan solo ve verificaciones de Gaitan"""
        self.client.force_authenticate(user=self.func_gaitan)
        response = self.client.get('/api/admin/verificaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['prestador_ref_id'], str(self.prov_gaitan.id))

    def test_departmental_consolidation(self):
        """Funcionario de Meta ve verificaciones de Gaitan y Villavo, pero no Medellin"""
        self.client.force_authenticate(user=self.func_meta)
        response = self.client.get('/api/admin/verificaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_national_oversight(self):
        """Admin ve todo"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/verificaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

    def test_rnt_integration_mock(self):
        """Prueba de integración RNT y subclasificación"""
        from apps.turismo.services.rnt_integration import RNTIntegrationService

        # Sincronizamos el prestador de Gaitan
        RNTIntegrationService.sync_provider(self.prov_gaitan.id)
        self.prov_gaitan.refresh_from_db()

        self.assertTrue(self.prov_gaitan.rnt_validated)
        self.assertEqual(self.prov_gaitan.status, 'ACTIVE')
        self.assertIsNotNone(self.prov_gaitan.rnt_last_sync)
