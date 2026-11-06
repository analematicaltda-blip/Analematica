# infrastructure/management/commands/seed_demo_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from infrastructure.models import Tenant
from funnels.models import Funnel, FunnelVersion
from funnels.runtime_models import Lead
from sales.models import Opportunity

class Command(BaseCommand):
    help = 'Seeds the database with demo data.'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        tenant, _ = Tenant.objects.get_or_create(name='Default Tenant')
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={'password': 'password'}
        )

        funnel, _ = Funnel.objects.get_or_create(
            tenant=tenant,
            name='Demo Funnel',
            defaults={'status': 'published'}
        )

        version, _ = FunnelVersion.objects.get_or_create(
            funnel=funnel,
            version_number=1,
            defaults={'schema_json': {'pages': []}, 'is_active': True}
        )

        for i in range(5):
            lead, _ = Lead.objects.get_or_create(
                funnel=funnel,
                initial_version=version,
                tenant=tenant,
                defaults={'form_data': {'email': f'lead{i}@example.com'}}
            )

        opportunities_data = [
            {'name': 'Initial CRM Implementation', 'stage': 'proposal', 'value': 15000.00},
            {'name': 'Marketing Campaign Q3', 'stage': 'negotiation', 'value': 7500.00},
            {'name': 'Website Redesign Project', 'stage': 'new', 'value': 12000.00},
        ]

        for opp_data in opportunities_data:
            opportunity, created = Opportunity.objects.get_or_create(
                name=opp_data['name'],
                tenant=tenant,
                defaults={
                    'stage': opp_data['stage'],
                    'value': opp_data['value'],
                    'assigned_to': user,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created opportunity: "{opportunity.name}"'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))
