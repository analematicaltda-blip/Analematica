from django.core.management.base import BaseCommand
from django.core.management import call_command
import csv
from apps.turismo.models.divipola import Department, Municipality
from django.conf import settings

class Command(BaseCommand):
    help = 'Seed DIVIPOLA Departments and Municipalities from CSV'

    def handle(self, *args, **options):
        csv_path = settings.BASE_DIR / 'backend/divipola.csv'  # Adjust path if needed

        depts = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dept_code = row['cod_dpto']
                dept_name = row['dpto']
                mun_code = row['cod_mpio']
                mun_name = row['nom_mpio']
                if dept_code not in depts:
                    dept, created = Department.objects.get_or_create(code=dept_code, defaults={'name': dept_name})
                    depts[dept_code] = dept
                    self.stdout.write(self.style.SUCCESS(f'Seed dept {dept_code} - {dept_name}'))
                else:
                    dept = depts[dept_code]

                Municipality.objects.update_or_create(
                    code=mun_code,
                    defaults={'name': mun_name, 'dept': dept}
                )

        self.stdout.write(self.style.SUCCESS('DIVIPOLA seeded successfully!'))
