import os
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import MenuItem

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

class Command(BaseCommand):
    """
    Este comando de Django limpia y crea los elementos del menú principal del sitio web
    para reflejar la nueva estructura organizacional.
    """
    help = 'Reorganiza el menú principal según la nueva estructura definida.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Limpiando la configuración de menú existente...'))
        MenuItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('¡Menú limpiado con éxito!'))

        self.stdout.write(self.style.NOTICE('Creando la nueva estructura del menú...'))

        # --- Nueva Estructura del Menú ---
        menu_data = [
            {
                "nombre": "Institucional", "url": "#", "children": [
                    {"nombre": "Secretaría de Turismo", "url": "/institucional/secretaria-turismo"},
                    {"nombre": "Dirección de Turismo", "url": "/institucional/direccion-turismo"},
                    {"nombre": "Consejo Municipal de Turismo", "url": "/institucional/consejo-turismo"},
                ]
            },
            {
                "nombre": "Descubre el Paraíso", "url": "#", "children": [
                    {"nombre": "Rutas Turísticas", "url": "/descubre/rutas-turisticas"},
                    {"nombre": "Atractivos", "url": "/descubre/atractivos"},
                    {"nombre": "Historia", "url": "/descubre/historia"},
                    {"nombre": "Cómo llegar", "url": "/descubre/como-llegar"},
                    {"nombre": "Mapa Interactivo", "url": "/descubre/mapa"},
                    {"nombre": "Agenda Cultural", "url": "/descubre/agenda-cultural"},
                    {"nombre": "Galería", "url": "/descubre/galeria"},
                ]
            },
            {
                "nombre": "Directorio", "url": "#", "children": [
                    {"nombre": "Prestadores de Servicios Turísticos", "url": "/directorio/prestadores"},
                    {"nombre": "Artesanos", "url": "/directorio/artesanos"},
                ]
            }
        ]

        self._create_menu_items_recursive(menu_data)

        self.stdout.write(self.style.SUCCESS('\n¡La nueva estructura del menú ha sido creada con éxito!'))

    def _create_menu_items_recursive(self, items, parent=None, level=0):
        """Función recursiva para crear elementos de menú anidados."""
        for index, item_data in enumerate(items):
            menu_item = MenuItem.objects.create(
                nombre=item_data['nombre'],
                url=item_data['url'],
                parent=parent,
                orden=index
            )
            indent = "  " * (level + 1)
            self.stdout.write(self.style.SUCCESS(f'{indent}- Creado: {menu_item.nombre}'))

            if 'children' in item_data and item_data['children']:
                self._create_menu_items_recursive(item_data['children'], parent=menu_item, level=level + 1)