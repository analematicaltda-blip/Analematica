from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser, Publicacion
from rest_framework.authtoken.models import Token

class ApprovalWorkflowAPITests(APITestCase):
    """
    Pruebas para el flujo de aprobación jerárquico de Publicaciones.
    Verifica que los estados cambien correctamente según el rol del usuario.
    """

    def setUp(self):
        # --- Crear usuarios con roles para el flujo de aprobación ---
        self.admin_user = CustomUser.objects.create_superuser(
            'admin_approver', 'admin_approver@example.com', 'password123'
        )
        self.directivo_user = CustomUser.objects.create_user(
            'directivo_approver', 'directivo_approver@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_DIRECTIVO
        )
        self.profesional_user = CustomUser.objects.create_user(
            'profesional_creator', 'profesional_creator@example.com', 'password123', role=CustomUser.Role.FUNCIONARIO_PROFESIONAL
        )

        # --- Crear tokens para autenticación ---
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.directivo_token = Token.objects.create(user=self.directivo_user)
        self.profesional_token = Token.objects.create(user=self.profesional_user)

        # --- Crear una publicación inicial en estado BORRADOR ---
        self.publicacion = Publicacion.objects.create(
            titulo="Evento de Prueba",
            slug="evento-de-prueba",
            tipo=Publicacion.Tipo.EVENTO,
            autor=self.profesional_user,
            estado=Publicacion.Status.BORRADOR
        )

        # --- URLs para las acciones ---
        # El basename para el ViewSet de admin es 'publicacion-admin'
        self.detail_url = reverse('publicacion-admin-detail', kwargs={'pk': self.publicacion.pk})
        self.submit_url = reverse('publicacion-admin-submit-for-approval', kwargs={'pk': self.publicacion.pk})
        self.approve_url = reverse('publicacion-admin-approve', kwargs={'pk': self.publicacion.pk})
        self.reject_url = reverse('publicacion-admin-reject', kwargs={'pk': self.publicacion.pk})

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_profesional_submits_for_approval(self):
        """Un Profesional puede enviar un borrador para aprobación, cambiando el estado a PENDIENTE_DIRECTIVO."""
        self.client.credentials(**self._get_auth_header(self.profesional_token))
        response = self.client.post(self.submit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Status.PENDIENTE_DIRECTIVO)

    def test_directivo_approves_to_admin(self):
        """Un Directivo puede aprobar una publicación, cambiando el estado a PENDIENTE_ADMIN."""
        self.publicacion.estado = Publicacion.Status.PENDIENTE_DIRECTIVO
        self.publicacion.save()

        self.client.credentials(**self._get_auth_header(self.directivo_token))
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Status.PENDIENTE_ADMIN)

    def test_admin_publishes(self):
        """Un Admin puede aprobar una publicación, cambiando el estado a PUBLICADO."""
        self.publicacion.estado = Publicacion.Status.PENDIENTE_ADMIN
        self.publicacion.save()

        self.client.credentials(**self._get_auth_header(self.admin_token))
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Status.PUBLICADO)

    def test_profesional_cannot_approve(self):
        """Un Profesional NO PUEDE aprobar una publicación pendiente de un directivo."""
        self.publicacion.estado = Publicacion.Status.PENDIENTE_DIRECTIVO
        self.publicacion.save()

        self.client.credentials(**self._get_auth_header(self.profesional_token))
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_directivo_can_reject(self):
        """Un Directivo puede rechazar una publicación, devolviéndola a BORRADOR."""
        self.publicacion.estado = Publicacion.Status.PENDIENTE_DIRECTIVO
        self.publicacion.save()

        self.client.credentials(**self._get_auth_header(self.directivo_token))
        response = self.client.post(self.reject_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Status.BORRADOR)

    def test_public_view_only_shows_published(self):
        """La vista pública NO debe mostrar publicaciones que no estén en estado PUBLICADO."""
        # Primero, verificamos que no se muestra en estado BORRADOR
        public_list_url = reverse('publicaciones-list')
        response = self.client.get(public_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # Ahora, la publicamos y verificamos que sí aparece
        self.publicacion.estado = Publicacion.Status.PUBLICADO
        self.publicacion.save()
        response = self.client.get(public_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.publicacion.id)