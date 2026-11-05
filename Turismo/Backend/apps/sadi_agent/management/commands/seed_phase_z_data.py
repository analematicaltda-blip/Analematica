# backend/apps/sadi_agent/management/commands/seed_phase_z_data.py
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import CustomUser
from apps.sadi_agent.models import SemanticDomain, Intent, Example, VoicePermission

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos iniciales para la Fase Z (semántica y permisos).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando el seeder de la Fase Z...'))

        self._create_semantic_data()
        self._create_voice_permissions()

        self.stdout.write(self.style.SUCCESS('¡Seeder de la Fase Z completado con éxito!'))

    def _create_semantic_data(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Dominios, Intenciones y Ejemplos Semánticos ---'))

        # Dominio de Prestadores
        prestadores_domain, created = SemanticDomain.objects.get_or_create(
            name='prestadores',
            defaults={'description': 'Dominio para la gestión de prestadores de servicios turísticos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Dominio '{prestadores_domain.name}' creado."))

        # Intención de Onboarding
        onboarding_intent, created = Intent.objects.get_or_create(
            domain=prestadores_domain,
            name='ONBOARDING_PRESTADOR',
            defaults={'description': 'Registrar un nuevo prestador en el sistema.'}
        )
        if created:
            self.stdout.write(f"  - Intención '{onboarding_intent.name}' creada.")

        # Ejemplos para la intención de Onboarding
        examples = [
            # Español
            {'text': "Registra un hotel llamado 'Hotel Paraíso' con correo contacto@hotelparaiso.com", 'language': 'es'},
            {'text': "Quiero dar de alta al proveedor 'Restaurante El Buen Sabor' con email info@buensabor.co", 'language': 'es'},

            # Inglés
            {'text': "Register a hotel called 'Paradise Hotel' with email contact@paradisehotel.com", 'language': 'en'},
            {'text': "I want to sign up the provider 'The Good Taste Restaurant' with email info@goodtaste.co", 'language': 'en'},

            # Portugués
            {'text': "Registre um hotel chamado 'Hotel Paraíso' com o email contato@hotelparaiso.com", 'language': 'pt'},
            {'text': "Quero cadastrar o fornecedor 'Restaurante Bom Sabor' com o email info@bomsabor.co", 'language': 'pt'},
        ]

        for ex_data in examples:
            example, created = Example.objects.get_or_create(
                intent=onboarding_intent,
                text=ex_data['text'],
                defaults={'language': ex_data['language']}
            )
            if created:
                self.stdout.write(f"    - Ejemplo '{example.text}' ({example.language}) creado.")

    def _create_voice_permissions(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Permisos de Voz ---'))

        permissions = [
            # El Administrador puede crear prestadores
            {'role': CustomUser.Role.ADMIN, 'domain': 'prestadores', 'action': 'ONBOARDING_PRESTADOR'},

            # El Turista NO puede crear prestadores
            # (La ausencia de un registro significa denegación)
        ]

        for perm_data in permissions:
            permission, created = VoicePermission.objects.get_or_create(
                role=perm_data['role'],
                domain=perm_data['domain'],
                action=perm_data['action']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Permiso creado: {permission}"))
