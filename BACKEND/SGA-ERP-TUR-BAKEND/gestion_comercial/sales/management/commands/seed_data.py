
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from infrastructure.models import Tenant
from sales.models import Opportunity
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with initial data for CRM verification.'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        User = get_user_model()

        # 1. Create Tenant
        tenant, created = Tenant.objects.get_or_create(name='Default Tenant')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant.name}" created.'))
        else:
            self.stdout.write(f'Tenant "{tenant.name}" already exists.')

        # 2. Create User
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'testuser@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'password123')

        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(email=email, password=password, tenant=tenant, is_staff=True, is_superuser=True)
            self.stdout.write(self.style.SUCCESS(f'User "{user.email}" created.'))
        else:
            user = User.objects.get(email=email)
            self.stdout.write(f'User "{user.email}" already exists.')

        # 3. Create Opportunities
        opportunities_to_create = [
            {'name': 'Gran Oportunidad de IA', 'company_name': 'Innovatech Global', 'value': 50000, 'stage': 'proposal', 'tenant': tenant},
            {'name': 'Proyecto de Marketing Digital', 'company_name': 'Marketing Masters', 'value': 25000, 'stage': 'negotiation', 'tenant': tenant},
            {'name': 'Nuevo Lead de E-commerce', 'company_name': 'Shopify Plus Experts', 'value': 10000, 'stage': 'new', 'tenant': tenant},
            {'name': 'Contacto de Conferencia', 'company_name': 'Quantum Dynamics', 'value': 15000, 'stage': 'contacted', 'tenant': tenant},
        ]

        for opp_data in opportunities_to_create:
            opportunity, created = Opportunity.objects.get_or_create(
                name=opp_data['name'],
                defaults=opp_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Opportunity "{opportunity.name}" created.'))
            else:
                self.stdout.write(f'Opportunity "{opportunity.name}" already exists.')

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
