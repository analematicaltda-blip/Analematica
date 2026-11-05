# SaritaUnificado/backend/api/management/commands/create_test_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.prestadores.models import Perfil, CategoriaPrestador
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un usuario de prueba de tipo PRESTADOR y su perfil asociado.'

    def handle(self, *args, **kwargs):
        username = os.environ.get('TEST_USER_USERNAME', 'prestador_test')
        email = os.environ.get('TEST_USER_EMAIL', 'prestador@test.com')
        password = os.environ.get('TEST_USER_PASSWORD', 'testpassword123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"El usuario '{username}' ya existe. Saltando creación."))
            return

        self.stdout.write(self.style.NOTICE(f"Creando usuario de prueba '{username}'..."))

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='PRESTADOR'
        )

        # Crea una categoría de ejemplo si no existe
        categoria, _ = CategoriaPrestador.objects.get_or_create(
            nombre='Hotel de Prueba',
            defaults={'slug': 'hotel-de-prueba'}
        )

        # Crea el perfil asociado
        Perfil.objects.create(
            usuario=user,
            nombre_comercial='Hotel Test Inn',
            categoria=categoria,
            estado='Activo'
        )

        self.stdout.write(self.style.SUCCESS(f"Usuario y perfil de prestador '{username}' creados con éxito."))
