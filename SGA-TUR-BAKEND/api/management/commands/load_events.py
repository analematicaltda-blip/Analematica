import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import Publicacion, CustomUser

class Command(BaseCommand):
    help = 'Carga los eventos, festivales y celebraciones iniciales a la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de eventos y celebraciones...'))

        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No se encontró un superusuario. Por favor, cree uno primero.'))
            return

        eventos = [
            # 1. Festivales y eventos principales
            {"titulo": "Puente de Reyes – Festival de Verano “Manacacías”", "fecha_inicio": "01-06", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Cumpleaños de Puerto Gaitán", "fecha_inicio": "02-11", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Festival Laguna de Oro (Vereda Carimagua 1)", "fecha_inicio": "02-16", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival de la Gallina Criolla (Vereda Carimagua 2)", "fecha_inicio": "03-01", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival (Vereda Tillava)", "fecha_inicio": "03-08", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival de la Cachera de Oro (San Pedro de Arimena)", "fecha_inicio": "03-25", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival Etnocultural y Deportivo El Cachirre de la Orinoquia (Resguardo Wacoyo)", "fecha_inicio": "03-29", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival Internacional de la Cachama", "fecha_inicio": "05-19", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Fiesta Patronal Catedral María Madre de la Iglesia", "fecha_inicio": "05-28", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "XVIII Festival del Zaino de Oro (Vereda La Cristalina)", "fecha_inicio": "09-15", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Fiesta Patronal El Divino Niño (Barrio Bateas)", "fecha_inicio": "09-16", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival de la Sabana (Vereda Murujuy)", "fecha_inicio": "10-15", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival Arte, Letras y Cultura “Desde las Tierras de las Toninas”", "fecha_inicio": "10-25", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Día de los Niños", "fecha_inicio": "10-31", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Festival de la Caramera de Oro (Vereda San Miguel)", "fecha_inicio": "11-10", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Encuentro Celebra la Música", "fecha_inicio": "11-22", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Encuentro Saberes Kulima (Resguardo Wacoyo)", "fecha_inicio": "11-30", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival de Velas y Faroles (Malecón Municipal)", "fecha_inicio": "12-07", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival del Chinchorro Mata Palo (Resguardo Awaliba)", "fecha_inicio": "12-07", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival del Alcaraván Llanero (Vereda Planas)", "fecha_inicio": "12-08", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival del Moriche (Vereda Porvenir)", "fecha_inicio": "12-08", "subcategoria": "FESTIVAL_PRINCIPAL"},
            {"titulo": "Festival El Espuelín de Oro (Vereda Puente Arimena)", "fecha_inicio": "12-22", "subcategoria": "FESTIVAL_PRINCIPAL"},

            # 2. Celebraciones especiales (Llaneridad)
            {"titulo": "Día de la Llaneridad", "fecha_inicio": "01-12", "subcategoria": "CELEBRACION_LLANERIDAD", "descripcion": "Celebración mensual de las tradiciones llaneras. Se repite cada mes."},

            # 3. Actividades culturales y cívicas anuales
            {"titulo": "Día del Padre", "fecha_inicio": "03-19", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día del Idioma", "fecha_inicio": "04-23", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día de la Danza (Celebra la Danza)", "fecha_inicio": "04-29", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Mes de la Niñez – Brújula Express", "fecha_inicio": "04-27", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Mes de las Madres (actividades culturales)", "fecha_inicio": "05-13", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día del Maestro", "fecha_inicio": "05-15", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Independencia de Colombia", "fecha_inicio": "07-20", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día Nacional de la Identidad Llanera", "fecha_inicio": "07-25", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Vacaciones recreativas y culturales", "fecha_inicio": "08-03", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día de los Pueblos Indígenas", "fecha_inicio": "08-09", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Mes del Adulto Mayor (celebración cultural)", "fecha_inicio": "08-28", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Día Nacional del Turismo", "fecha_inicio": "09-27", "subcategoria": "ACTIVIDAD_CIVICA"},
            {"titulo": "Celebraciones navideñas", "fecha_inicio": "12-20", "subcategoria": "ACTIVIDAD_CIVICA"},
        ]

        current_year = datetime.date.today().year
        count = 0
        for evento_data in eventos:
            titulo = evento_data["titulo"]
            fecha_str = f'{current_year}-{evento_data["fecha_inicio"]}'
            fecha_inicio = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')

            # Para la celebración mensual de la llaneridad, creamos 12 eventos
            if evento_data["subcategoria"] == "CELEBRACION_LLANERIDAD":
                for i in range(1, 13):
                    mes_titulo = f"Día de la Llaneridad - {fecha_inicio.replace(month=i).strftime('%B')}"
                    slug = slugify(f"{mes_titulo}-{current_year}-{i}")
                    _, created = Publicacion.objects.get_or_create(
                        slug=slug,
                        defaults={
                            'titulo': mes_titulo,
                            'tipo': 'EVENTO',
                            'subcategoria_evento': evento_data["subcategoria"],
                            'contenido': evento_data.get("descripcion", "Detalles por confirmar."),
                            'fecha_evento_inicio': fecha_inicio.replace(month=i),
                            'estado': Publicacion.Status.PUBLICADO,
                            'autor': admin_user,
                        }
                    )
                    if created:
                        count += 1
            else:
                slug = slugify(f"{titulo}-{fecha_inicio.strftime('%B')}-{current_year}")
                _, created = Publicacion.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'titulo': titulo,
                        'tipo': 'EVENTO',
                        'subcategoria_evento': evento_data["subcategoria"],
                        'contenido': 'Detalles del evento por confirmar.',
                        'fecha_evento_inicio': fecha_inicio,
                        'estado': Publicacion.Status.PUBLICADO,
                        'autor': admin_user,
                    }
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se crearon {count} nuevos eventos y celebraciones.'))