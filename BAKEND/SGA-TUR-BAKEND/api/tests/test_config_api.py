from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser, SiteConfiguration, MenuItem
from rest_framework.authtoken.models import Token

class SiteConfigurationAPITests(APITestCase):
    """
    Pruebas para el endpoint de SiteConfiguration.
    Verifica que la lectura sea pública y la escritura restringida a Admins.
    """
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = CustomUser.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.funcionario_user = CustomUser.objects.create_user('funcionario', 'func@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO)
        self.turista_user = CustomUser.objects.create_user('turista', 'turista@example.com', 'password123', role=CustomUser.Role.TURISTA)

        # Crear tokens para autenticación
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.funcionario_token = Token.objects.create(user=self.funcionario_user)
        self.turista_token = Token.objects.create(user=self.turista_user)

        # Cargar la configuración inicial
        self.config = SiteConfiguration.load()
        self.url = reverse('site-configuration')

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_get_config_is_public(self):
        """Cualquier usuario, incluso no autenticado, puede ver la configuración."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('direccion', response.data)

    def test_update_config_as_admin(self):
        """Un admin PUEDE actualizar la configuración."""
        data = {'direccion': 'Nueva Calle 123'}
        response = self.client.patch(self.url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.config.refresh_from_db()
        self.assertEqual(self.config.direccion, 'Nueva Calle 123')

    def test_update_config_as_funcionario_is_forbidden(self):
        """Un funcionario NO PUEDE actualizar la configuración."""
        data = {'direccion': 'Calle Prohibida'}
        response = self.client.patch(self.url, data, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_config_as_turista_is_forbidden(self):
        """Un turista NO PUEDE actualizar la configuración."""
        data = {'direccion': 'Calle Prohibida'}
        response = self.client.patch(self.url, data, **self._get_auth_header(self.turista_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MenuItemAPITests(APITestCase):
    """
    Pruebas para el ViewSet de MenuItem.
    Verifica que la lectura sea pública y la escritura restringida a Admins.
    """
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.funcionario_user = CustomUser.objects.create_user('funcionario', 'func@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO)

        self.admin_token = Token.objects.create(user=self.admin_user)
        self.funcionario_token = Token.objects.create(user=self.funcionario_user)

        # Crear elementos de menú para probar
        self.parent_item = MenuItem.objects.create(nombre='Quienes Somos', url='/quienes-somos', orden=1)
        self.child_item = MenuItem.objects.create(nombre='Historia', url='/historia', parent=self.parent_item, orden=1)

        self.list_url = reverse('menu-item-list')
        self.detail_url = reverse('menu-item-detail', kwargs={'pk': self.parent_item.pk})

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_list_menu_items_is_public(self):
        """Cualquier usuario puede listar los elementos del menú (solo los padres)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta paginada contiene los resultados en la clave 'results'
        top_level_items_count = MenuItem.objects.filter(parent__isnull=True).count()
        self.assertEqual(len(response.data['results']), top_level_items_count)
        self.assertTrue(any(item['nombre'] == 'Quienes Somos' for item in response.data['results']))

    def test_create_menu_item_as_admin(self):
        """Un admin PUEDE crear un elemento de menú."""
        initial_count = MenuItem.objects.count()
        data = {'nombre': 'Contacto', 'url': '/contacto', 'orden': 2}
        response = self.client.post(self.list_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), initial_count + 1)

    def test_create_menu_item_as_funcionario_is_forbidden(self):
        """Un funcionario NO PUEDE crear un elemento de menú."""
        data = {'nombre': 'Contacto', 'url': '/contacto', 'orden': 2}
        response = self.client.post(self.list_url, data, **self._get_auth_header(self.funcionario_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_menu_item_as_admin(self):
        """Un admin PUEDE actualizar un elemento de menú."""
        data = {'nombre': 'Sobre Nosotros'}
        response = self.client.patch(self.detail_url, data, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parent_item.refresh_from_db()
        self.assertEqual(self.parent_item.nombre, 'Sobre Nosotros')

    def test_delete_menu_item_as_admin(self):
        """Un admin PUEDE eliminar un elemento de menú."""
        # Primero, eliminamos todos los items para hacer la prueba robusta
        MenuItem.objects.all().delete()
        # Creamos un item para poder eliminarlo
        item_to_delete = MenuItem.objects.create(nombre='Para Borrar', url='/borrar')
        detail_url = reverse('menu-item-detail', kwargs={'pk': item_to_delete.pk})

        response = self.client.delete(detail_url, **self._get_auth_header(self.admin_token))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MenuItem.objects.count(), 0)

    def test_reorder_menu_items(self):
        """Un admin puede reordenar y anidar elementos del menú."""
        # Estado inicial: parent_item (Quienes Somos), child_item (Historia)
        item3 = MenuItem.objects.create(nombre='Contacto', url='/contacto', orden=2)

        # Nueva estructura:
        # 1. Contacto
        # 2. Quienes Somos
        #    - Historia
        new_structure = [
            {'id': item3.id, 'children': []},
            {'id': self.parent_item.id, 'children': [
                {'id': self.child_item.id, 'children': []}
            ]}
        ]

        reorder_url = reverse('menu-item-reorder')
        response = self.client.post(reorder_url, new_structure, format='json', **self._get_auth_header(self.admin_token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar la nueva estructura en la base de datos
        item3.refresh_from_db()
        self.parent_item.refresh_from_db()
        self.child_item.refresh_from_db()

        self.assertEqual(item3.orden, 0)
        self.assertEqual(item3.parent, None)

        self.assertEqual(self.parent_item.orden, 1)
        self.assertEqual(self.parent_item.parent, None)

        self.assertEqual(self.child_item.orden, 0)
        self.assertEqual(self.child_item.parent, self.parent_item)