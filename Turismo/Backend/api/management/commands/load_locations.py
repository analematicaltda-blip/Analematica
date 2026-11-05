import csv
from django.core.management.base import BaseCommand
from api.models import Department, Municipality
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Carga departamentos y municipios desde un archivo CSV de DIVIPOLA.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='La ruta al archivo CSV que contiene los datos de DIVIPOLA.')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']
        self.stdout.write(self.style.NOTICE(f"Iniciando la carga de ubicaciones desde {file_path}..."))

        self.stdout.write(self.style.WARNING("Eliminando datos existentes de municipios y departamentos para asegurar una carga limpia..."))
        Municipality.objects.all().delete()
        Department.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Datos anteriores eliminados."))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                departments_cache = {}
                municipalities_created_count = 0
                departments_created_count = 0

                for row in reader:
                    department_name = row.get('dpto')
                    municipality_name = row.get('nom_mpio')

                    if not department_name or not municipality_name:
                        self.stdout.write(self.style.WARNING(f"Omitiendo fila por datos faltantes: {row}"))
                        continue

                    department_name = department_name.strip().title()
                    municipality_name = municipality_name.strip().title()

                    department = departments_cache.get(department_name)
                    if not department:
                        department, created = Department.objects.get_or_create(name=department_name)
                        departments_cache[department_name] = department
                        if created:
                            departments_created_count += 1

                    _, created = Municipality.objects.get_or_create(
                        name=municipality_name,
                        department=department
                    )
                    if created:
                        municipalities_created_count += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: El archivo {file_path} no fue encontrado."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Proceso completado. Departamentos creados: {departments_created_count}. Municipios creados: {municipalities_created_count}."
        ))