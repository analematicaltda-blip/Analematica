from django.core.management.base import BaseCommand
from api.models import Video

class Command(BaseCommand):
    help = 'Carga los videos de ejemplo a la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de videos de ejemplo...'))

        videos = [
            {
                "titulo": "Comida Típica de Puerto Gaitán",
                "descripcion": "Un breve recorrido por los sabores y platos tradicionales de nuestro municipio. ¡Una delicia para el paladar!",
                "url": "https://www.youtube.com/watch?v=hfcK9pb-FWI"
            },
            {
                "titulo": "Corto sobre la Comida de Puerto Gaitán",
                "descripcion": "Descubre la riqueza gastronómica de Puerto Gaitán en este corto visual.",
                "url": "https://www.youtube.com/watch?v=s6vSrjDciP0"
            },
            {
                "titulo": "Festival de Verano Manacacías",
                "descripcion": "Vive la emoción y la alegría del Festival de Verano Manacacías, un evento que celebra nuestra cultura y naturaleza.",
                "url": "https://www.youtube.com/watch?v=tMyhPDTy4vo"
            },
            {
                "titulo": "Sendero Ecoturístico Sikuani",
                "descripcion": "Acompáñanos en un viaje por el sendero Sikuani y descubre la profunda conexión de nuestras comunidades indígenas con la naturaleza.",
                "url": "https://www.youtube.com/watch?v=1JeB2TuBXHU"
            },
            {
                "titulo": "Experiencia en la Granja Villareal",
                "descripcion": "Conoce la Granja Villareal, un ejemplo de agroturismo y sostenibilidad en el corazón de los Llanos.",
                "url": "https://www.youtube.com/watch?v=G_VTKq7rGP8"
            },
            {
                "titulo": "Un Día en la Granja El Edén",
                "descripcion": "Descubre la vida en la Granja El Edén, un proyecto de soberanía alimentaria y amor por la tierra.",
                "url": "https://www.youtube.com/watch?v=hnm0CdntBC4"
            },
            {
                "titulo": "Puerto Gaitán: Un Paraíso por Descubrir (Versión Larga)",
                "descripcion": "Un documental completo que explora la belleza, cultura y biodiversidad de Puerto Gaitán, el paraíso natural de Colombia.",
                "url": "https://www.youtube.com/watch?v=PedKx3umYD8"
            },
            {
                "titulo": "Puerto Gaitán: Un Paraíso por Descubrir (Versión Corta)",
                "descripcion": "Un vistazo rápido y emocionante a las maravillas que te esperan en Puerto Gaitán.",
                "url": "https://www.youtube.com/watch?v=G_kKE-k3_8k"
            }
        ]

        count = 0
        for video_data in videos:
            _, created = Video.objects.get_or_create(
                url_youtube=video_data["url"],
                defaults={
                    'titulo': video_data["titulo"],
                    'descripcion': video_data["descripcion"],
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'  - Añadido video: "{video_data["titulo"]}"'))

        self.stdout.write(self.style.SUCCESS(f'\nProceso completado. Se añadieron {count} nuevos videos.'))