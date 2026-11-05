
from django.core.management.base import BaseCommand
from apps.web_funnel.models import WebPage, Section, ContentBlock

class Command(BaseCommand):
    help = 'Crea una página de inicio de ejemplo para el embudo de ventas dinámico.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la creación de la página de inicio...'))

        # Eliminar contenido existente para evitar duplicados
        WebPage.objects.filter(slug='inicio').delete()

        # Crear la página principal
        home_page = WebPage.objects.create(
            title='Potencia tu Negocio Turístico con Sarita',
            slug='inicio',
            is_published=True
        )

        # Crear una sección "Hero"
        hero_section = Section.objects.create(
            web_page=home_page,
            title='Tu Aliado Digital en el Turismo',
            order=1
        )

        # Añadir bloques de contenido a la sección "Hero"
        ContentBlock.objects.create(
            section=hero_section,
            content_type='text',
            content='Descubre la plataforma todo-en-uno que simplifica la gestión, mejora la visibilidad y conecta tu negocio con el mundo.',
            order=1
        )
        ContentBlock.objects.create(
            section=hero_section,
            content_type='button',
            content='Ver Planes y Precios',
            link='/decision',
            order=2
        )

        # Crear una sección de "Beneficios"
        benefits_section = Section.objects.create(
            web_page=home_page,
            title='Beneficios Clave',
            order=2
        )

        ContentBlock.objects.create(
            section=benefits_section,
            content_type='text',
            content='- **Gestión Integral:** Controla operaciones, finanzas y marketing desde un solo lugar.\n- **Visibilidad Aumentada:** Conéctate con el ecosistema turístico local y global.\n- **Decisiones Inteligentes:** Accede a datos y reportes para optimizar tu negocio.',
            order=1
        )

        self.stdout.write(self.style.SUCCESS(f'Página "{home_page.title}" creada exitosamente.'))

        # --- Crear Página de Consideración (MOFU) ---
        WebPage.objects.filter(slug='consideracion').delete()
        mofu_page = WebPage.objects.create(
            title='¿Por qué Sarita es la elección correcta?',
            slug='consideracion',
            is_published=True
        )
        mofu_section = Section.objects.create(
            web_page=mofu_page,
            title='Testimonios de Clientes',
            order=1
        )
        ContentBlock.objects.create(
            section=mofu_section,
            content_type='text',
            content='"Desde que usamos Sarita, nuestra eficiencia operativa ha aumentado en un 40%. La gestión de reservas y la comunicación con los turistas nunca ha sido tan fácil."\n- Hotel Paraíso',
            order=1
        )
        ContentBlock.objects.create(
            section=mofu_section,
            content_type='button',
            content='Ver todos los planes',
            link='/decision',
            order=2
        )
        self.stdout.write(self.style.SUCCESS(f'Página "{mofu_page.title}" creada exitosamente.'))
