
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_contable.activos_fijos.models import CategoriaActivo, ActivoFijo

class ActivosFijosAPITestCase(TestCase):
    def setUp(self):
        # Crear usuarios
        self.prestador_user = CustomUser.objects.create_user(username='prestador', email='prestador@test.com', password='password', role='PRESTADOR')
        self.admin_user = CustomUser.objects.create_superuser(username='admin', email='admin@test.com', password='password')

        # Crear perfiles
        self.prestador_profile = ProviderProfile.objects.create(usuario=self.prestador_user, nombre_comercial='Hotel Test')

        # Refrescar el objeto de usuario para obtener la relación inversa
        self.prestador_user.refresh_from_db()

        # Clientes de API
        self.client_prestador = APIClient()
        self.client_prestador.force_authenticate(user=self.prestador_user)

        self.client_admin = APIClient()
        self.client_admin.force_authenticate(user=self.admin_user)

    def test_crear_activo_sin_owner_lo_asigna_al_prestador_actual(self):
        """Prueba que crear un activo sin especificar un owner lo asigna al perfil del usuario actual."""
        response = self.client_prestador.post('/api/v1/mi-negocio/contable/activos-fijos/categorias/', {
            'nombre': 'Mobiliario'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        categoria = CategoriaActivo.objects.get(pk=response.data['id'])
        self.assertEqual(categoria.owner, self.prestador_profile)

    def test_admin_puede_crear_activo_con_owner_valido(self):
        """Prueba que un admin puede crear un activo y asignarle un owner polimórfico."""
        owner_content_type = ContentType.objects.get_for_model(ProviderProfile)
        data = {
            'nombre': 'Equipo de Oficina (Admin)',
            'owner': {
                'type': f'{owner_content_type.app_label}.{owner_content_type.model}',
                'id': self.prestador_profile.pk
            }
        }
        response = self.client_admin.post('/api/v1/mi-negocio/contable/activos-fijos/categorias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        categoria = CategoriaActivo.objects.get(pk=response.data['id'])
        self.assertEqual(categoria.owner, self.prestador_profile)

    def test_crear_activo_con_owner_invalido_falla(self):
        """Prueba que la creación falla si el owner no existe."""
        owner_content_type = ContentType.objects.get_for_model(ProviderProfile)
        data = {
            'nombre': 'Activo Fantasma',
            'owner': {
                'type': f'{owner_content_type.app_label}.{owner_content_type.model}',
                'id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'  # UUID inexistente
            }
        }
        response = self.client_admin.post('/api/v1/mi-negocio/contable/activos-fijos/categorias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prestador_no_puede_asignar_owner(self):
        """Prueba que un usuario no-admin no puede asignar un owner, incluso si es válido."""
        owner_content_type = ContentType.objects.get_for_model(ProviderProfile)
        data = {
            'nombre': 'Intento de Asignación',
            'owner': {
                'type': f'{owner_content_type.app_label}.{owner_content_type.model}',
                'id': self.prestador_profile.pk
            }
        }
        response = self.client_prestador.post('/api/v1/mi-negocio/contable/activos-fijos/categorias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leer_activo_devuelve_estructura_owner_correcta(self):
        """Prueba que la lectura de un activo devuelve el campo owner normalizado."""
        categoria = CategoriaActivo.objects.create(nombre='Vehículos', owner=self.prestador_profile)
        response = self.client_prestador.get(f'/api/v1/mi-negocio/contable/activos-fijos/categorias/{categoria.pk}/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        owner_data = response.data['owner_details']
        owner_content_type = ContentType.objects.get_for_model(ProviderProfile)

        self.assertIsNotNone(owner_data)
        self.assertEqual(owner_data['type'], f'{owner_content_type.app_label}.{owner_content_type.model}')
        self.assertEqual(owner_data['id'], str(self.prestador_profile.pk))

    def test_activos_antiguos_con_perfil_son_visibles(self):
        """Prueba de compatibilidad hacia atrás: los activos creados solo con `perfil` son visibles."""
        # Crear un activo al estilo antiguo, solo con el campo `perfil`
        categoria_antigua = CategoriaActivo.objects.create(nombre='Mobiliario Antiguo', perfil=self.prestador_profile)

        # La API debería listar este activo antiguo gracias a la consulta con Q objects
        response = self.client_prestador.get('/api/v1/mi-negocio/contable/activos-fijos/categorias/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el activo antiguo está en la lista
        ids_en_respuesta = [item['id'] for item in response.data['results']]
        self.assertIn(categoria_antigua.id, ids_en_respuesta)
