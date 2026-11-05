from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from api.models import (
    CustomUser, RubroArtesano, Artesano,
    RutaTuristica, MenuItem, AtractivoTuristico, Publicacion, ContenidoMunicipio
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador
from apps.web_funnel.models import WebPage # Importar WebPage

class Command(BaseCommand):
    help = 'Crea o actualiza datos de prueba para el sistema, incluyendo todo el contenido de la plataforma. Es idempotente.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga masiva de contenido...'))

        admin_user = self._create_base_users_and_categories()
        self._create_rutas_turisticas()
        self._create_atractivos_turisticos()
        self._associate_content()
        self._create_publicaciones(admin_user)
        self._create_contenido_municipio()
        self._create_menu()
        self._create_web_pages() # Añadir llamada a la nueva función

        self.stdout.write(self.style.SUCCESS('\n¡Proceso de carga masiva de contenido completado!'))

    def _create_web_pages(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Páginas Web Públicas (Web Funnel) ---'))
        WebPage.objects.get_or_create(
            slug='inicio',
            defaults={
                'title': 'Página de Inicio de Sarita',
                'is_published': True
            }
        )
        self.stdout.write(self.style.SUCCESS("Página de prueba 'inicio' creada."))

    def _create_menu(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Reestructurando el Menú Principal ---'))

        # Borrar el menú existente para asegurar una estructura limpia
        MenuItem.objects.all().delete()
        self.stdout.write(self.style.WARNING('Menú anterior eliminado.'))

        # Crear nueva estructura de menú
        menu_structure = [
            {'nombre': 'Quiénes somos', 'url': '/quienes-somos', 'orden': 1, 'children': [
                {'nombre': 'Secretaría de Turismo', 'url': '/quienes-somos#secretaria', 'orden': 1},
            ]},
            {'nombre': 'Generalidades del municipio', 'url': '/generalidades-municipio', 'orden': 2},
            {'nombre': 'Directorio', 'url': '#', 'orden': 3, 'children': [
                {'nombre': 'Prestadores de Servicio Turístico', 'url': '/prestadores', 'orden': 1},
                {'nombre': 'Artesanos', 'url': '/artesanos', 'orden': 2},
            ]},
            {'nombre': 'Atractivos', 'url': '/atractivos', 'orden': 4},
            {'nombre': 'Agenda cultural', 'url': '/agenda-cultural', 'orden': 5},
            {'nombre': 'Blog de Noticias', 'url': '/noticias', 'orden': 6},
            {'nombre': 'Cómo Llegar', 'url': '/como-llegar', 'orden': 7},
        ]

        for item_data in menu_structure:
            children_data = item_data.pop('children', None)
            parent, created = MenuItem.objects.get_or_create(
                nombre=item_data['nombre'],
                defaults=item_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Menú principal '{parent.nombre}' creado."))

            if children_data:
                for child_data in children_data:
                    MenuItem.objects.get_or_create(
                        nombre=child_data['nombre'],
                        parent=parent,
                        defaults=child_data
                    )
                    self.stdout.write(f"  - Submenú '{child_data['nombre']}' creado.")

    def _create_contenido_municipio(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Contenido del Municipio ---'))

        contenidos = [
            {
                'seccion': ContenidoMunicipio.Seccion.INTRODUCCION,
                'titulo': 'Datos Generales del Municipio',
                'contenido': """Puerto Gaitán es uno de los municipios más importantes del departamento del Meta..."""
            },
            {
                'seccion': ContenidoMunicipio.Seccion.UBICACION_CLIMA,
                'titulo': 'Ubicación y Clima',
                'contenido': """Puerto Gaitán está ubicado en los Llanos Orientales de Colombia..."""
            },
            {
                'seccion': ContenidoMunicipio.Seccion.ALOJAMIENTO,
                'titulo': 'Dónde Dormir',
                'contenido': """Puerto Gaitán ofrece una amplia gama de opciones de alojamiento..."""
            },
            {
                'seccion': ContenidoMunicipio.Seccion.COMO_LLEGAR,
                'titulo': 'Cómo Llegar',
                'contenido': """**En Coche:** Desde Bogotá, tomar la Autopista al Llano..."""
            },
            {
                'seccion': ContenidoMunicipio.Seccion.CONTACTOS,
                'titulo': 'Información Importante',
                'contenido': """**Policía Nacional:** +57 320 7307009..."""
            },
            {
                'seccion': ContenidoMunicipio.Seccion.FINANZAS,
                'titulo': 'Entidades Financieras',
                'contenido': """**Banco de Bogotá:** Cra. 13 #7 – 50..."""
            }
        ]

        for idx, data in enumerate(contenidos):
            _, created = ContenidoMunicipio.objects.get_or_create(
                seccion=data['seccion'],
                titulo=data['titulo'],
                defaults={
                    'contenido': data['contenido'],
                    'orden': idx,
                    'es_publicado': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Contenido para la sección '{data['titulo']}' creado."))

    def _create_base_users_and_categories(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Usuarios y Categorías Base ---'))
        CategoriaPrestador.objects.get_or_create(nombre='Hoteles', defaults={'slug': 'hoteles'})
        CategoriaPrestador.objects.get_or_create(nombre='Restaurantes', defaults={'slug': 'restaurantes'})
        RubroArtesano.objects.get_or_create(nombre='Tejidos', defaults={'slug': 'tejidos'})

        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Usuarios de Prueba para Roles ---'))

        test_users = {
            'admin_test': {'role': CustomUser.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
            'sadi': {'role': CustomUser.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
            'turista_test': {'role': CustomUser.Role.TURISTA},
            'prestador_test': {'role': CustomUser.Role.PRESTADOR},
            'artesano_test': {'role': CustomUser.Role.ARTESANO},
            'directivo_test': {'role': CustomUser.Role.FUNCIONARIO_DIRECTIVO},
            'profesional_test': {'role': CustomUser.Role.FUNCIONARIO_PROFESIONAL},
        }

        for username, data in test_users.items():
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'role': data['role'],
                    'is_staff': data.get('is_staff', False),
                    'is_superuser': data.get('is_superuser', False)
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario de prueba '{username}' creado."))

        # Devolvemos el usuario administrador principal para otras funciones
        return CustomUser.objects.get(username='admin_test')

    def _create_rutas_turisticas(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando y Actualizando Rutas Turísticas ---'))
        rutas_data = {
            'ruta-gastronomica': {'nombre': 'Ruta Turismo Gastronómico', 'descripcion': 'Descubre los sabores únicos de la gastronomía llanera.'},
            'ruta-agroturismo': {'nombre': 'Ruta Agroturismo', 'descripcion': 'Vive la experiencia del campo y aprende sobre nuestras tradiciones agrícolas.'},
            'ruta-etnoturismo': {'nombre': 'Ruta Etnoturismo', 'descripcion': 'Conéctate con la cultura y las tradiciones de nuestras comunidades indígenas.'},
            'ruta-biciturismo': {'nombre': 'Ruta Bici turismo', 'descripcion': 'Recorre paisajes increíbles sobre dos ruedas.'},
            'ruta-urbana': {'nombre': 'Ruta Zona Urbana', 'descripcion': 'Explora la historia y los lugares emblemáticos del casco urbano de Puerto Gaitán.'},
            'ruta-folclor': {'nombre': 'Ruta Folclor Llanero', 'descripcion': 'Sumérgete en la música, el baile y las costumbres del folclor llanero.'},
            'ruta-avistamiento': {'nombre': 'Ruta de Avistamiento', 'descripcion': 'Maravíllate con la diversidad de aves y fauna de la región.'}
        }

        for slug, data in rutas_data.items():
            RutaTuristica.objects.update_or_create(slug=slug, defaults={'nombre': data['nombre'], 'descripcion': data['descripcion'], 'es_publicado': True})

    def _create_atractivos_turisticos(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Atractivos Turísticos ---'))
        atractivos_data = [
            {'nombre': 'Finca La Peluza', 'descripcion': 'Sumérgete en el mundo de la agroecología...', 'categoria_color': 'BLANCO'},
            {'nombre': 'Finca Ebenezer', 'descripcion': 'Descubre la tradición y la innovación...', 'categoria_color': 'BLANCO'},
        ]
        for data in atractivos_data:
            AtractivoTuristico.objects.get_or_create(slug=slugify(data['nombre']), defaults={'nombre': data['nombre'], 'descripcion': data['descripcion'], 'categoria_color': data['categoria_color'], 'es_publicado': True})

    def _associate_content(self):
        self.stdout.write(self.style.HTTP_INFO('\n--- Asociando Atractivos con Rutas ---'))
        associations = {'ruta-agroturismo': ['finca-la-peluza', 'finca-ebenezer']}
        for ruta_slug, atractivo_slugs in associations.items():
            try:
                ruta = RutaTuristica.objects.get(slug=ruta_slug)
                atractivos = AtractivoTuristico.objects.filter(slug__in=atractivo_slugs)
                ruta.atractivos.set(atractivos)
            except RutaTuristica.DoesNotExist:
                pass

    def _create_publicaciones(self, author):
        self.stdout.write(self.style.HTTP_INFO('\n--- Creando Publicaciones de Blog y Noticias ---'))
        publicaciones_data = [
            {'tipo': 'BLOG', 'titulo': 'Cómo hacer aviturismo por primera vez', 'contenido': 'El aviturismo es una experiencia fascinante...'},
            {'tipo': 'NOTICIA', 'titulo': 'Fin de semana de música y cultura en Puerto Gaitán, Meta', 'contenido': 'Del 10 al 12 de mayo de 2024...'},
        ]
        for data in publicaciones_data:
            Publicacion.objects.get_or_create(slug=slugify(data['titulo']), defaults={'tipo': data['tipo'], 'titulo': data['titulo'], 'contenido': data['contenido'], 'autor': author, 'estado': Publicacion.Status.PUBLICADO})