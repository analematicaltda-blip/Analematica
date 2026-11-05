from django.core.management.base import BaseCommand
from apps.defense_deception.models import GhostSurface

class Command(BaseCommand):
    help = 'S-3.1: Seed Ghost Surfaces for Deception Layer'

    def handle(self, *args, **options):
        surfaces = [
            {'name': 'Honeypot Admin Login', 'path': '/api/admin/v1/auth/root/', 'deception_type': 'HONEYPOT_LOGIN'},
            {'name': 'Fake DB Export', 'path': '/api/v1/mi-negocio/backup/full/', 'deception_type': 'SIMULATED_DB_EXPORT'},
            {'name': 'Sensitive Config API', 'path': '/api/v1/kernel/config/secrets/', 'deception_type': 'FAKE_API'},
        ]

        for s in surfaces:
            GhostSurface.objects.get_or_create(name=s['name'], defaults=s)

        self.stdout.write(self.style.SUCCESS('PDE/ADL: Superficies Fantasma desplegadas exitosamente.'))
