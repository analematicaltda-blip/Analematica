import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import Publicacion, CustomUser

class Command(BaseCommand):
    help = 'Carga los artículos de Blog y Noticias de ejemplo a la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de artículos y noticias...'))

        admin_user, _ = CustomUser.objects.get_or_create(
            username='nelson@suonos.co',
            defaults={'email': 'nelson@suonos.co', 'is_staff': True, 'role': 'FUNCIONARIO'}
        )
        sara_user, _ = CustomUser.objects.get_or_create(
            username='Sara Sierra',
            defaults={'email': 'sara@example.com', 'is_staff': True, 'role': 'FUNCIONARIO'}
        )

        articles = [
            # BLOGS
            {
                "tipo": "BLOG",
                "titulo": "Cómo hacer aviturismo por primera vez",
                "contenido": """<p>El aviturismo es una experiencia fascinante que conecta a los amantes de la naturaleza con la observación de aves en su hábitat natural. Si eres nuevo en este mundo y deseas explorar las maravillas de la naturaleza, escogiste el lugar perfecto para aprender. Esta guía te ayudará a comenzar a y disfrutar al máximo de esta experiencia.</p>
                <p>Para realizar aviturismo lo primero que debes tener es actitud positiva por aprender, pues debes estudiar acerca del nombre y apariencia de las aves que se encuentran en Puerto Gaitán ya sea locales o migratorias.</p>
                <h4>1. Preparar tu equipo básico</h4>
                <p>Lo bueno de realizar aviturismo es que no requieres de grandes inversiones, contar con el equipo adecuado hará tu experiencia más placentera. Estos son los elementos esenciales:</p>
                <ul>
                    <li><strong>Binoculares:</strong> son tu herramienta principal para observar aves a distancia. Busca un modelo con aumento de 8×42, que ofrece una combinación ideal entre campo de visión y claridad.</li>
                    <li><strong>Guía de aves:</strong> Lleva una guía de campo puede ser un libro físico o una aplicación móvil.</li>
                    <li><strong>Ropa cómoda:</strong> opta por prendas de colores neutros, como verde o beige, que te ayuden a camuflarte.</li>
                    <li><strong>Snacks y bebidas:</strong> algunos recorridos pueden ser largos y extensos, por lo que es importante llevar comida y agua.</li>
                </ul>
                <h4>2. Aprende a moverte cuidadosamente</h4>
                <p>El secreto para disfrutar de este tipo de turismo está en el respeto hacia la naturaleza. Debes moverte lentamente y mantener silencio.</p>
                <h4>3. Ten paciencia y disfruta</h4>
                <p>Finalmente, ten paciencia pues algunas aves se asustan o permanecen ocultas por mucho tiempo.</p>""",
                "autor": admin_user, "fecha_publicacion": "2025-02-17"
            },
            {
                "tipo": "BLOG", "titulo": "Como adentrarse al universo Sikuani",
                "contenido": """<p>Los Sikuani, también conocidos como Guahibos, es un pueblo indígena que habita los territorios del Orinoco, principalmente en Colombia y Venezuela.</p><p>Su ideología está arraigada profundamente con la madre tierra, en especial con su árbol sagrado llamado Kaliawirinae, considerado como el árbol de la vida. Pues es el origen de todo tanto de los alimentos como de la vida misma.</p><p>Su espiritualidad es el eje central de esta comunidad, donde, mediante rituales, pueden comunicarse con sus ancestros. Los Payes (guías espirituales) son los encargados de transmitir sus conocimientos y velar por el equilibrio espiritual de la comunidad.</p>""",
                "autor": admin_user, "fecha_publicacion": "2025-02-17"
            },
            {
                "tipo": "BLOG", "titulo": "Visita las fincas agroecológicas de Puerto Gaitán",
                "contenido": """<p>¿Te gustaría visitar una finca agroecológica pero no sabes dónde? ¡Pues llegaste al lugar indicado! En este blog encontrarás las fincas agroecológicas que Puerto Gaitán tiene para ti.</p><h4>Finca La Peluza</h4><p>Esta finca ofrece experiencias únicas, desde recorridos por sus apiarios, biofábrica y huertas agroecológicas, hasta actividades prácticas como recoger ingredientes frescos de la huerta.</p><h4>Finca Ebenezer</h4><p>Ven y visita a doña Rubiela y su familia. Ellos cultivan cacao, cúrcuma y borojó. Puedes aprender sobre la elaboración artesanal de chocolate.</p><h4>Finca Villa Real</h4><p>Rodeada de frutales, esta finca liderada por Nancy y su esposo ofrece un recorrido educativo por cultivos de guayaba, cúrcuma y café.</p><h4>Finca El Edén</h4><p>Ubicada en la vereda Guasipaty. Con un enfoque en el “buen vivir” y la soberanía alimentaria, esta finca combina recorridos cortos por cultivos de cítricos y cúrcuma.</p>""",
                "autor": sara_user, "fecha_publicacion": "2025-02-17"
            },
            {
                "tipo": "BLOG", "titulo": "Cómo disfrutar un fin de semana en pareja en Puerto Gaitán",
                "contenido": """<p>Cuando buscamos un destino para compartir momentos únicos e inolvidables en pareja, Puerto Gaitán se presenta como una opción perfecta. En este bello municipio podrás llevar a cabo actividades que combinan diversión, naturaleza y tranquilidad.</p><h4>Día 1: Encuentro con la naturaleza y un atardecer llanero</h4><p>No hay mejor opción que comenzar explorando diversos lugares naturales, entre ellos el río Manacacías, donde, además de observar aves y animales locales, podrás admirar las emblemáticas toninas (delfines rosados).</p><h4>Día 2: Deporte y experiencias agroecológicas</h4><p>¿Qué mejor manera de conocer Puerto Gaitán que en bicicleta? Diseñada especialmente para ti, la ruta biciturística urbana te permitirá descubrir los distintos atractivos turísticos que este bello municipio tiene para ofrecer.</p>""",
                "autor": admin_user, "fecha_publicacion": "2025-02-17"
            },
            {
                "tipo": "BLOG", "titulo": "La Tonina y Su Vida Social",
                "contenido": """<p>En Sudamérica habitan siete tipos de especies de delfines una de ellas es la (Inia geoffrensis) conocidamente como tonina o delfín rosado. Esta especie puede llegar a pesar 180 kilos y medir 2,8 metros de longitud. Convirtiéndose en el mamífero de río más grande del planeta.</p><p>Los delfines son animales muy sociales y pueden llegar a vivir más de 40 años. En el caso de las toninas, pueden formar familias o grupos de hasta 20 mamíferos, en donde se reúnen en lugares donde se alimentan y se reproducen, como las confluencias de los ríos.</p>""",
                "autor": admin_user, "fecha_publicacion": "2024-10-05"
            },
            {
                "tipo": "BLOG", "titulo": "Gastronomía de los Llanos",
                "contenido": """<p>La gastronomía es otro aspecto indispensable del folclor llanero. Platos como la mamona o carne a la llanera, el pisillo y la cachapa son el reflejo de una cocina auténtica, que aprovecha los recursos locales y en la que se celebran los sabores de la tierra.</p>""",
                "autor": sara_user, "fecha_publicacion": "2024-10-04"
            },
            {
                "tipo": "BLOG", "titulo": "El Folclor Llanero",
                "contenido": """<h4>Poesía y Leyendas</h4><p>La poesía y las leyendas llaneras forman parte esencial de la cultura oral de la región. En las noches de fogata, los habitantes comparten historias sobre personajes míticos como el Silbón o la Llorona.</p><h4>Vestimenta Tradicional</h4><p>La vestimenta tradicional también es un símbolo del folclor llanero. Los hombres, con su sombrero de ala ancha, pantalón arremangado y alpargatas, y las mujeres, con faldas amplias y coloridas, representan la sencillez.</p><h4>Canto de Vaquería</h4><p>El canto de vaquería es otro pilar del folclor llanero, una tradición que se remonta a los tiempos en que los vaqueros guiaban el ganado por las vastas llanuras.</p>""",
                "autor": admin_user, "fecha_publicacion": "2024-10-03"
            },
             {
                "tipo": "BLOG", "titulo": "Reserva Natural Mururito: Ejemplo de Conservación",
                "contenido": """<p>Este lugar ubicado en Puerto Gaitán, Meta, demuestra la posibilidad de escoger un camino diferente, hacia la conservación y el ecoturismo, donde el agua es la prioridad.</p><p>Mientras Mururito está rodeada de plantaciones de eucaliptos, de pinos, de cultivos de aceite de palma y de ganadería extensiva, desde 2006 la Finca Hotel Ecológica Mururito Reserva Natural emprende un camino hacia la conservación.</p><p>En esta tierra de 2000 hectáreas, en una curva del Río Manacacías, los inventarios de aves, ranas y las cámaras trampas para el monitoreo de la fauna demuestran como se pudo conservar la gran riqueza y biodiversidad del lugar.</p>""",
                "autor": sara_user, "fecha_publicacion": "2024-10-01"
            },
            # NOTICIAS
            {
                "tipo": "NOTICIA", "titulo": "Fenómeno solar sorprende a los habitantes de Puerto Gaitán",
                "contenido": """<p>Los cielos del municipio de Puerto Gaitán, Meta, ofrecieron un espectáculo inusual que captó la atención de sus habitantes: el sol está rodeado por un círculo luminoso, conocido como halo solar.</p><p>Este fenómeno óptico ocurre cuando la luz del sol pasa a través de cristales de hielo suspendidos en nubes altas, como cirros o cirrostratos, formando un anillo de luz alrededor del astro.</p>""",
                "autor": admin_user, "fecha_publicacion": "2024-09-28"
            },
            {
                "tipo": "NOTICIA", "titulo": "Fin de semana de música y cultura en Puerto Gaitán, Meta",
                "contenido": """<p>Del 10 al 12 de mayo de 2024, Puerto Gaitán, Meta, es epicentro de la cultura y la música. Por medio de una programación amplia y diversa, «la perla del Manacacías» rinde tributo al folclor y las tradiciones del pueblo llanero a través de la imagen del pez más representativo de la región: la cachama.</p><p>Los actos musicales del Festival de Puerto Gaitán en 2024 incluyen la participación de artistas de repercusión internacional como Blessd, Fonseca, Jessi Uribe, Yeison Jiménez y Peter Manjarrés.</p>""",
                "autor": admin_user, "fecha_publicacion": "2024-05-08"
            }
        ]

        count = 0
        for data in articles:
            slug = slugify(data['titulo'])
            # Asegurar slug único
            unique_slug = slug
            num = 1
            while Publicacion.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{slug}-{num}'
                num += 1

            _, created = Publicacion.objects.get_or_create(
                slug=unique_slug,
                defaults={
                    'titulo': data['titulo'],
                    'contenido': data['contenido'],
                    'tipo': data['tipo'],
                    'autor': data['autor'],
                    'fecha_publicacion': data['fecha_publicacion'],
                    'estado': Publicacion.Status.PUBLICADO,
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'  - Creado: "{data["titulo"]}"'))

        self.stdout.write(self.style.SUCCESS(f'\nProceso completado. Se crearon {count} nuevos artículos.'))