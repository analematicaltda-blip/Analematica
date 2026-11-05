# funnels/management/commands/seed_funnel_data.py

import json
from django.core.management.base import BaseCommand
from django.db import transaction
from infrastructure.models import Tenant, User
from funnels.models import CadenaTurismo, Categoria, Subcategoria, LandingPage, Funnel, FunnelVersion

# Datos extraídos del frontend (data.ts) para la siembra
CADENAS_DATA = [
    {'id': 1, 'nombre': 'Restaurantes', 'color_primario': '#d97706', 'color_secundario': '#fef3c7'},
    {'id': 2, 'nombre': 'Hoteles', 'color_primario': '#0e7490', 'color_secundario': '#ecfeff'},
]
CATEGORIAS_DATA = [
    {'id': 1, 'cadena_id': 1, 'nombre': 'Comida Tradicional / Típica', 'icon': '🍛'},
    {'id': 2, 'cadena_id': 2, 'nombre': 'Alojamientos por Tipo o Enfoque', 'icon': '🏕️'},
]
SUBCATEGORIAS_DATA = [
    {'id': 1, 'categoria_id': 1, 'nombre': 'Cocina regional (ej. llanera, paisa, costeña)'},
    {'id': 2, 'categoria_id': 2, 'nombre': 'Ecohoteles y Alojamiento Sostenible'},
]
LANDING_PAGES_DATA = [
    {'id': 1, 'subcategoria_id': 2, 'nombre': 'Landing Principal Ecohotel', 'publicada': True},
    {'id': 2, 'subcategoria_id': 1, 'nombre': 'Landing Asados Llaneros', 'publicada': True},
]
FUNNELS_DATA = [
    {'id': 1, 'landing_page_id': 1, 'name': 'Reservas Ecohotel'},
    {'id': 2, 'landing_page_id': 2, 'name': 'Reservas Parrillada'},
]
# Este es un ejemplo del schema_json que el frontend espera.
# En una implementación real, sería mucho más complejo.
FUNNEL_SCHEMA_EXAMPLE = {
    "pages": [
        {
            "id": "fp-1629882928131-0.5",
            "name": "Página de Oferta",
            "path": "/oferta",
            "type": "offer",
            "blocks": [
                {
                    "id": "blk-1629882928131-0.6",
                    "type": "hero",
                    "name": "Hero Block",
                    "order": 1,
                    "props": {
                        "title": {"value": "Título desde el Backend", "type": "string"},
                        "subtitle": {"value": "Este contenido se cargó desde la base de datos.", "type": "longtext"}
                    },
                    "styles": {"textAlign": "center"},
                    "responsive": {}
                }
            ]
        }
    ],
    "theme": {
        "font": {"headings": "Inter", "body": "Inter"},
        "colors": {"primary": "#0e7490", "secondary": "#ecfeff"}
    }
}

class Command(BaseCommand):
    help = 'Seeds the database with initial data for the Funnel Builder'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')

        # 1. Crear Tenant y Usuario de prueba
        tenant, _ = Tenant.objects.get_or_create(name='Tenant de Prueba')

        # Usar create_user para asegurar el hasheo de la contraseña
        user_email = 'test@example.com'
        if not User.objects.filter(email=user_email).exists():
            user = User.objects.create_user(
                email=user_email,
                password='testpassword',
                tenant=tenant
            )
            self.stdout.write(f'User "{user.email}" created.')
        else:
            user = User.objects.get(email=user_email)
            self.stdout.write(f'User "{user.email}" already exists.')

        self.stdout.write(f'Tenant "{tenant.name}" and User "{user.email}" are ready.')

        # 2. Poblar la jerarquía
        for data in CADENAS_DATA:
            CadenaTurismo.objects.get_or_create(id=data['id'], tenant=tenant, defaults=data)
        for data in CATEGORIAS_DATA:
            Categoria.objects.get_or_create(id=data['id'], defaults=data)
        for data in SUBCATEGORIAS_DATA:
            Subcategoria.objects.get_or_create(id=data['id'], defaults=data)
        for data in LANDING_PAGES_DATA:
            LandingPage.objects.get_or_create(id=data['id'], defaults=data)

        self.stdout.write('Hierarchy (Cadenas, Categorias, etc.) seeded.')

        # 3. Crear Funnels y su primera versión con el schema
        for data in FUNNELS_DATA:
            funnel, created = Funnel.objects.get_or_create(
                id=data['id'],
                tenant=tenant,
                defaults=data
            )
            if created:
                FunnelVersion.objects.create(
                    funnel=funnel,
                    version_number=1,
                    schema_json=FUNNEL_SCHEMA_EXAMPLE
                )

        self.stdout.write('Funnels and their initial versions seeded.')
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
