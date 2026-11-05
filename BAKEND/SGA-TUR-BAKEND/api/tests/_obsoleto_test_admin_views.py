from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser, ContenidoMunicipio
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador, Perfil
from rest_framework.authtoken.models import Token

class AdminAPITests(APITestCase):
    """
    Pruebas actualizadas para los endpoints de administración, usando el nuevo modelo Perfil.
    """
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='password123'
        )
        self.funcionario_user = CustomUser.objects.create_user(
            username='funcionario', email='funcionario@example.com', password='password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO
        )
        self.prestador_user_to_approve = CustomUser.objects.create_user(
            username='prestador_pendiente', email='pendiente@example.com', password='password123', role=CustomUser.Role.PRESTADOR
        )
        self.turista_user = CustomUser.objects.create_user(
            username='turista', email='turista@example.com', password='password123', role=CustomUser.Role.TURISTA
        )

        self.categoria = CategoriaPrestador.objects.create(nombre="Hotel", slug="hoteles")
        # Usando el nuevo modelo 'Perfil' en lugar de 'PrestadorServicio'
        self.prestador_profile = Perfil.objects.create(
            usuario=self.prestador_user_to_approve,
            nombre_comercial="Hotel La Roca",
            categoria=self.categoria
        )

        self.admin_token = Token.objects.create(user=self.admin_user)
        self.funcionario_token = Token.objects.create(user=self.funcionario_user)
        self.turista_token = Token.objects.create(user=self.turista_user)

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_list_prestadores_as_admin(self):
        url = reverse('admin-prestador-list')
        response = self.client.get(url, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_prestadores_as_funcionario(self):
        url = reverse('admin-prestador-list')
        response = self.client.get(url, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_prestadores_as_turista_is_forbidden(self):
        url = reverse('admin-prestador-list')
        response = self.client.get(url, **self._get_auth_header(self.turista_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ContenidoMunicipioAPITests(APITestCase):
    """
    Pruebas para el ViewSet de ContenidoMunicipio, verificando permisos mixtos.
    """
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.turista_user = CustomUser.objects.create_user(
            'turista', 'turista@test.com', 'password', role=CustomUser.Role.TURISTA
        )

        self.admin_token = Token.objects.create(user=self.admin_user)
        self.turista_token = Token.objects.create(user=self.turista_user)

        self.contenido = ContenidoMunicipio.objects.create(
            seccion=ContenidoMunicipio.Seccion.INTRODUCCION,
            titulo="Bienvenidos a Puerto Gaitán",
            contenido="Un paraíso por descubrir.",
            orden=1
        )
        self.list_url = reverse('contenido-municipio-list')
        self.detail_url = reverse('contenido-municipio-detail', kwargs={'pk': self.contenido.pk})

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_public_can_list_content(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta ahora puede estar paginada
        self.assertEqual(len(response.data['results']), 1)

    def test_admin_can_create_content(self):
        initial_count = ContenidoMunicipio.objects.count()
        data = {
            'seccion': ContenidoMunicipio.Seccion.ALOJAMIENTO,
            'titulo': 'Hoteles de Lujo',
            'contenido': 'Descripción de hoteles.',
            'orden': 2
        }
        response = self.client.post(self.list_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContenidoMunicipio.objects.count(), initial_count + 1)

    def test_turista_cannot_create_content(self):
        initial_count = ContenidoMunicipio.objects.count()
        data = {'seccion': 'OTRA', 'titulo': 'Intento', 'contenido': '...'}
        response = self.client.post(self.list_url, data, **self._get_auth_header(self.turista_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ContenidoMunicipio.objects.count(), initial_count)

    def test_admin_can_update_content(self):
        data = {'titulo': 'Nuevo Título'}
        response = self.client.patch(self.detail_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contenido.refresh_from_db()
        self.assertEqual(self.contenido.titulo, 'Nuevo Título')

    def test_admin_can_delete_content(self):
        initial_count = ContenidoMunicipio.objects.count()
        response = self.client.delete(self.detail_url, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ContenidoMunicipio.objects.count(), initial_count - 1)
