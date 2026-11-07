import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import urllib.request
from api.models import PaginaInstitucional, CustomUser

class Command(BaseCommand):
    """
    Este comando de Django crea o actualiza las páginas institucionales con contenido predefinido.
    Es útil para poblar el sitio con datos iniciales de forma consistente.
    """
    help = 'Crea o actualiza el contenido de las páginas institucionales.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando la creación de contenido para páginas institucionales...'))

        # Se necesita un usuario autor para asociar los registros.
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin_setup',
            defaults={'is_staff': True, 'is_superuser': True, 'role': 'ADMIN'}
        )
        if created:
            admin_user.set_password('adminpassword')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Creado usuario administrador para la configuración inicial.'))

        # --- Definición del Contenido de las Páginas ---
        paginas_data = [
            {
                "slug": "secretaria-turismo",
                "nombre": "Secretaría de Turismo y Desarrollo Económico",
                "titulo_banner": "Turismo y Desarrollo para Puerto Gaitán",
                "subtitulo_banner": "Impulsando el crecimiento de nuestra región.",
                "contenido_principal": "Nuestra misión es formular y ejecutar políticas, planes y proyectos que promuevan el desarrollo turístico y económico sostenible de Puerto Gaitán, posicionándolo como un destino competitivo a nivel nacional e internacional.",
                "programas_proyectos": "Actualmente, lideramos iniciativas como el 'Corredor Turístico del Manacacías', programas de formalización para prestadores de servicios y la 'Ruta del Amanecer Llanero', buscando diversificar la oferta y mejorar la calidad de los servicios.",
                "estrategias_apoyo": "Ofrecemos capacitaciones constantes en marketing digital, servicio al cliente y gestión empresarial. Además, facilitamos el acceso a microcréditos y promovemos la participación de nuestros empresarios en ferias y eventos nacionales.",
            },
            {
                "slug": "direccion-turismo",
                "nombre": "Dirección de Turismo",
                "titulo_banner": "Descubre el Paraíso Natural",
                "subtitulo_banner": "Tu aventura en Puerto Gaitán comienza aquí.",
                "contenido_principal": "La Dirección de Turismo es la encargada de ejecutar las estrategias de promoción y regulación de la actividad turística en el municipio. Trabajamos de la mano con la comunidad y los prestadores para garantizar una experiencia inolvidable y sostenible para nuestros visitantes.",
                "programas_proyectos": "Gestionamos los Puntos de Información Turística (PIT), desarrollamos la señalización turística bilingüe y coordinamos los grandes eventos como el Festival de Verano. También mantenemos actualizada la oferta turística en este portal.",
                "estrategias_apoyo": "Fomentamos la creación de alianzas estratégicas entre hoteles, restaurantes y operadores turísticos para crear paquetes y experiencias integradas. Realizamos seguimiento constante para asegurar el cumplimiento de las normativas de calidad y formalidad.",
            },
            {
                "slug": "consejo-consultivo",
                "nombre": "Consejo Consultivo de Turismo",
                "titulo_banner": "Participación y Transparencia",
                "subtitulo_banner": "Construyendo juntos el futuro del turismo.",
                "contenido_principal": "El Consejo Consultivo de Turismo es un órgano de participación ciudadana y concertación entre los sectores público y privado. Su principal objetivo es asesorar a la administración municipal en la formulación e implementación de las políticas y planes de desarrollo turístico.",
                "programas_proyectos": "El Consejo se reúne de forma periódica para discutir temas clave como la promoción del destino, la mejora de la infraestructura, la sostenibilidad y la capacitación del talento humano. Las actas y decisiones de cada sesión son públicas y se pueden consultar en esta sección.",
                "estrategias_apoyo": "A través del Consejo, se canalizan las inquietudes y propuestas de la comunidad y los empresarios para asegurar que las estrategias de turismo sean inclusivas y respondan a las necesidades reales del sector. Fomentamos un diálogo abierto para fortalecer nuestro destino.",
            },
            {
                "slug": "historia-cultura",
                "nombre": "Historia y Cultura",
                "titulo_banner": "Corazón del Paraíso Natural",
                "subtitulo_banner": "Un legado de tradición y naturaleza.",
                "contenido_principal": "Puerto Gaitán, fundado oficialmente en 1932, es un crisol de culturas donde convergen las tradiciones de los pueblos indígenas Sikuani y Achagua con el espíritu llanero. Su historia está ligada a los ríos Manacacías, Meta y Yucao, que han sido testigos de su crecimiento desde un pequeño caserío hasta convertirse en el epicentro petrolero y turístico de la altillanura colombiana.",
                "programas_proyectos": "La cultura de Puerto Gaitán vibra al ritmo del joropo. Nuestras tradiciones se manifiestan en la gastronomía, con platos como la mamona y el pescado moqueado; en la música, con el arpa, el cuatro y los capachos; y en las danzas, que narran las historias del trabajo en el llano. El Festival Internacional de la Cachama y el Festival de Verano son las máximas expresiones de nuestra identidad cultural.",
                "estrategias_apoyo": "Personajes como Guadalupe Salcedo, líder de las guerrillas llaneras, marcaron la historia de nuestra región. Hoy, lugares como la Catedral María Madre de la Iglesia, el Malecón Ecoturístico y el Puente sobre el río Manacacías son testimonios de nuestro desarrollo. Invitamos a todos a explorar la riqueza cultural que Puerto Gaitán tiene para ofrecer.",
            }
        ]

        for data in paginas_data:
            pagina, created = PaginaInstitucional.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'nombre': data['nombre'],
                    'titulo_banner': data['titulo_banner'],
                    'subtitulo_banner': data['subtitulo_banner'],
                    'contenido_principal': data['contenido_principal'],
                    'programas_proyectos': data['programas_proyectos'],
                    'estrategias_apoyo': data['estrategias_apoyo'],
                    'actualizado_por': admin_user,
                }
            )

            # Descargar y asignar una imagen de banner si es una nueva página
            if created:
                self.stdout.write(self.style.SUCCESS(f'Creada página: "{pagina.nombre}"'))
                try:
                    # Usamos una imagen de placeholder
                    url = f'https://source.unsplash.com/1600x900/?nature,colombia,landscape'
                    with urllib.request.urlopen(url) as response:
                        content = response.read()
                        file_name = f"{pagina.slug}_banner.jpg"
                        pagina.banner.save(file_name, ContentFile(content), save=True)
                        self.stdout.write(self.style.SUCCESS(f'  -> Banner de ejemplo descargado y asignado.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  -> Error al descargar el banner: {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'Página "{pagina.nombre}" ya existía, no se modificó.'))

        self.stdout.write(self.style.SUCCESS('\n¡Proceso de creación de contenido completado!'))