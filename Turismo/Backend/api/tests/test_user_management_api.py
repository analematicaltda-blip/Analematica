from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser
from rest_framework.authtoken.models import Token


class UserManagementAPITests(APITestCase):
    """
    Pruebas para el endpoint de gestión de usuarios (/api/admin/users/).
    Verifica los permisos granulares para roles ADMIN y FUNCIONARIO.
    """
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        # --- Crear usuarios con diferentes roles ---
        self.admin_user = CustomUser.objects.create_superuser(
            'admin', 'admin@example.com', 'password123'
        )
        self.funcionario_user = CustomUser.objects.create_user(
            'funcionario1', 'func1@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO
        )
        self.funcionario_user_2 = CustomUser.objects.create_user(
            'funcionario2', 'func2@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO
        )
        self.turista_user = CustomUser.objects.create_user(
            'turista', 'turista@example.com', 'password123', role=CustomUser.Role.TURISTA
        )
        self.prestador_user = CustomUser.objects.create_user(
            'prestador', 'prestador@example.com', 'password123', role=CustomUser.Role.PRESTADOR
        )

        # --- Crear tokens para autenticación ---
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.funcionario_token = Token.objects.create(user=self.funcionario_user)

        # --- URLs ---
        self.list_url = reverse('user-admin-list')
        self.turista_detail_url = reverse('user-admin-detail', kwargs={'pk': self.turista_user.pk})
        self.admin_detail_url = reverse('user-admin-detail', kwargs={'pk': self.admin_user.pk})
        self.funcionario_detail_url = reverse('user-admin-detail', kwargs={'pk': self.funcionario_user_2.pk})

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    # === Pruebas para el rol ADMIN ===

    def test_admin_can_list_all_users(self):
        """Un ADMIN PUEDE listar todos los usuarios."""
        response = self.client.get(self.list_url, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)  # creados en setUp

    def test_admin_can_create_any_user(self):
        """Un ADMIN PUEDE crear un usuario con cualquier rol."""
        data = {'username': 'nuevofuncionario', 'password': 'password123', 'role': CustomUser.Role.FUNCIONARIO_DIRECTIVO}
        response = self.client.post(self.list_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username='nuevofuncionario').exists())

    def test_admin_can_update_any_user(self):
        """Un ADMIN PUEDE actualizar cualquier usuario."""
        data = {'email': 'turista_actualizado@example.com'}
        response = self.client.patch(self.turista_detail_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.turista_user.refresh_from_db()
        self.assertEqual(self.turista_user.email, 'turista_actualizado@example.com')

    def test_admin_can_delete_any_user(self):
        """Un ADMIN PUEDE eliminar cualquier usuario."""
        initial_count = CustomUser.objects.count()
        response = self.client.delete(self.turista_detail_url, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), initial_count - 1)

    # === Pruebas para el rol FUNCIONARIO ===

    def test_funcionario_can_list_allowed_users(self):
        """Un FUNCIONARIO PUEDE listar, pero solo ve TURISTAS, PRESTADORES y a sí mismo."""
        response = self.client.get(self.list_url, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('turista', usernames)
        self.assertIn('prestador', usernames)
        self.assertIn('funcionario1', usernames)
        self.assertNotIn('admin', usernames)
        self.assertNotIn('funcionario2', usernames)

    def test_funcionario_can_create_allowed_roles(self):
        """Un FUNCIONARIO PUEDE crear usuarios con rol TURISTA o PRESTADOR."""
        data_turista = {'username': 'nuevoturista', 'password': 'password123', 'role': 'TURISTA'}
        response = self.client.post(self.list_url, data_turista, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_funcionario_cannot_create_disallowed_roles(self):
        """Un FUNCIONARIO NO PUEDE crear usuarios con rol ADMIN o FUNCIONARIO."""
        data_admin = {'username': 'intentoadmin', 'password': 'password123', 'role': 'ADMIN'}
        response = self.client.post(self.list_url, data_admin, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data_func = {'username': 'intentofunc', 'password': 'password123', 'role': 'FUNCIONARIO_DIRECTIVO'}
        response = self.client.post(self.list_url, data_func, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_funcionario_can_update_allowed_user(self):
        """Un FUNCIONARIO PUEDE actualizar un usuario TURISTA o PRESTADOR."""
        data = {'email': 'turista_actualizado_por_func@example.com'}
        response = self.client.patch(self.turista_detail_url, data, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.turista_user.refresh_from_db()
        self.assertEqual(self.turista_user.email, 'turista_actualizado_por_func@example.com')

    def test_funcionario_cannot_update_disallowed_user(self):
        """Un FUNCIONARIO NO PUEDE actualizar un ADMIN u otro FUNCIONARIO."""
        data = {'email': 'intento_fallido@example.com'}
        response = self.client.patch(self.admin_detail_url, data, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(self.funcionario_detail_url, data, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_funcionario_can_delete_allowed_user(self):
        """Un FUNCIONARIO PUEDE eliminar un usuario TURISTA."""
        initial_count = CustomUser.objects.count()
        response = self.client.delete(self.turista_detail_url, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), initial_count - 1)

    def test_funcionario_cannot_delete_disallowed_user(self):
        """Un FUNCIONARIO NO PUEDE eliminar un ADMIN u otro FUNCIONARIO."""
        initial_count = CustomUser.objects.count()
        response = self.client.delete(self.admin_detail_url, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(self.funcionario_detail_url, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(CustomUser.objects.count(), initial_count)