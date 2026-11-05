import string
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import AtractivoTuristico, ImagenAtractivo, CustomUser

class Command(BaseCommand):
    help = 'Carga los atractivos turísticos iniciales a la base de datos, incluyendo imágenes de ejemplo.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de atractivos turísticos...'))

        # Se necesita un usuario autor (Admin o Funcionario) para asociar los registros.
        # Usaremos el primer superusuario que encontremos.
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No se encontró un superusuario. Por favor, cree uno primero.'))
            return

        atractivos = [
            # 🟨 Culturales e históricos
            {"nombre": "Arco monumento “Puerta al llano”", "categoria": "AMARILLO"},
            {"nombre": "Artesanías de indígenas Sikuani, Piapoco, Achawas, Sálibas", "categoria": "AMARILLO"},
            {"nombre": "Biblioteca Municipal Diana Turbay", "categoria": "AMARILLO"},
            {"nombre": "Festival Internacional de la Cachama", "categoria": "AMARILLO"},
            {"nombre": "Catedral María Madre de la Iglesia", "categoria": "AMARILLO"},
            {"nombre": "Las Bocas del Río Yucao, Meta y Manacaías", "categoria": "AMARILLO"},
            {"nombre": "Observatorio Ecológico Malecón", "categoria": "AMARILLO"},
            {"nombre": "Playas sobre el Río Manacacías", "categoria": "AMARILLO"},
            {"nombre": "Festival del Cachirre Wacoyo", "categoria": "AMARILLO"},
            {"nombre": "Resguardo Indígena Sikuani", "categoria": "AMARILLO"},
            {"nombre": "Tumba de Guadalupe Salcedo", "categoria": "AMARILLO"},
            {"nombre": "Iglesia San José Obrero", "categoria": "AMARILLO"},

            # 🟥 Parques y escenarios urbanos
            {"nombre": "Parque Jorge Eliecer Gaitán", "categoria": "ROJO"},
            {"nombre": "Parque el Malecón de Puerto Gaitán", "categoria": "ROJO"},
            {"nombre": "Manacacías Festival de Verano", "categoria": "ROJO"},
            {"nombre": "Manga de Coleo de San Pedro de Arimena", "categoria": "ROJO"},
            {"nombre": "Parque Principal Guadalupe Salcedo", "categoria": "ROJO"},
            {"nombre": "Edificación Ranchón Majagüillo", "categoria": "ROJO"},
            {"nombre": "Centro de Convenciones UNUMA", "categoria": "ROJO"},
            {"nombre": "Puente Trampolín", "categoria": "ROJO"},
            {"nombre": "Parque “Las Hamacas”", "categoria": "ROJO"},

            # ⬜ Naturales y otros atractivos
            {"nombre": "Río Yucao", "categoria": "BLANCO"},
            {"nombre": "Río Manacacías", "categoria": "BLANCO"},
            {"nombre": "Playa “La Española”", "categoria": "BLANCO"},
            {"nombre": "Playa “Sopla Vientos”", "categoria": "BLANCO"},
            {"nombre": "Playa “Chaviva”", "categoria": "BLANCO"},
            {"nombre": "Humedal Maiciana Manacal", "categoria": "BLANCO"},
            {"nombre": "Laguna “Las Maracas”", "categoria": "BLANCO"},
            {"nombre": "Laguna “El Caribe”", "categoria": "BLANCO"},
            {"nombre": "Laguna “Las Delicias”", "categoria": "BLANCO"},
            {"nombre": "Laguna Carimagua", "categoria": "BLANCO"},
            {"nombre": "Mirador “Solpavientos”", "categoria": "BLANCO"},
            {"nombre": "Inspección San Pedro de Arimena", "categoria": "BLANCO"},
        ]

        # Mapeo de categorías a palabras clave para Unsplash
        image_keywords = {
            "AMARILLO": "culture,history,colombia",
            "ROJO": "city,park,colombia",
            "BLANCO": "nature,river,colombia,landscape",
        }

        count = 0
        for atractivo_data in atractivos:
            nombre = atractivo_data["nombre"]
            slug_base = slugify(nombre)
            slug_final = slug_base
            suffix = 1
            while AtractivoTuristico.objects.filter(slug=slug_final).exists():
                slug_final = f"{slug_base}-{suffix}"
                suffix += 1

            atractivo, created = AtractivoTuristico.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'slug': slug_final,
                    'descripcion': f'Descripción de {nombre}. Este contenido debe ser completado por un funcionario.',
                    'como_llegar': f'Instrucciones sobre cómo llegar a {nombre}. Este contenido debe ser completado.',
                    'categoria_color': atractivo_data["categoria"],
                    'autor': admin_user
                }
            )

            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'  - Creado atractivo: "{nombre}"'))

                # Añadir imágenes de ejemplo
                if not atractivo.imagenes.exists():
                    self.stdout.write(self.style.HTTP_INFO(f'    -> Añadiendo imágenes de ejemplo...'))
                    keywords = image_keywords.get(atractivo.categoria_color, "colombia")
                    for i in range(3):
                        try:
                            # Usamos un tamaño específico y una semilla aleatoria para variedad
                            url = f'https://source.unsplash.com/800x600/?{keywords}&sig={string.digits + string.ascii_letters}'
                            with urllib.request.urlopen(url) as response:
                                content = response.read()
                                imagen_nombre = f'{slug_final}_{i+1}.jpg'

                                img = ImagenAtractivo(
                                    atractivo=atractivo,
                                    alt_text=f'Imagen de ejemplo para {nombre}'
                                )
                                img.imagen.save(imagen_nombre, ContentFile(content), save=True)
                                self.stdout.write(self.style.SUCCESS(f'      - Imagen {i+1} guardada.'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'      - Error descargando imagen {i+1}: {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Ya existe atractivo: "{nombre}"'))

        self.stdout.write(self.style.SUCCESS(f'\nProceso completado. Se crearon {count} nuevos atractivos turísticos.'))