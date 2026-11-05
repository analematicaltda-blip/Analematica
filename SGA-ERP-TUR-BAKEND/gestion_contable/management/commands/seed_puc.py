from django.core.management.base import BaseCommand
from django.apps import apps
import re

PUC_DATA = """
1	ACTIVO
11	DISPONIBLE
1105	CAJA
110505	CAJA GENERAL
# ... (full list truncated for brevity - paste full PUC here)
""".strip().split('\n')  # REPLACE WITH FULL PUC TEXT

Account = apps.get_model('core_erp', 'Account')

class Command(BaseCommand):
    help = 'Seed full PUC Colombian Chart of Accounts'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, required=True)

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        parents = {}
        for line in PUC_DATA:
            if not line.strip(): continue
            parts = line.split('\t')
            code = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ''
            level = len(code)
            parent_code = code[:-1] if level > 1 else None
            parent = parents.get(parent_code) if parent_code else None

            acc, created = Account.objects.get_or_create(
                tenant_id=tenant_id,
                code=code,
                defaults={'name': name, 'parent_account': parent, 'type': self.get_type(code), 'is_active': True}
            )
            parents[code] = acc
            self.stdout.write(self.style.SUCCESS(f'Seeded {code} - {name}'))
        self.stdout.write(self.style.SUCCESS('PUC seeding complete'))

    def get_type(self, code):
        cls = code[0]
        if cls in ['1']: return 'asset'
        if cls in ['2']: return 'liability'
        # Add all mappings
        return 'other'

