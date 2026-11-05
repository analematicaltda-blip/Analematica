from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import RubroArtesano
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador

class Command(BaseCommand):
    help = 'Seeds 500+ sub-classifications for Tourism and Delivery'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando despliegue de subclasificaciones...")

        # 1. Hotels (50)
        self.seed_subclass('hotel', [
            'Hotel Boutique', 'Hotel de Lujo', 'Hotel Económico', 'Hotel Cápsula', 'Hotel Temático',
            'Hotel Ecológico', 'Hotel Sostenible', 'Hotel Inteligente', 'Hotel de Diseño', 'Hotel Histórico',
            'Hotel de Playa', 'Hotel de Ciudad', 'Hotel Rural', 'Hotel de Montaña', 'Selva Lodge',
            'Hotel Aeropuerto', 'Hotel Carretera', 'Hotel Flotante', 'Isla Resort', 'Hotel Desierto',
            'All Inclusive', 'Media Pensión', 'Solo Alojamiento', 'Bed and Breakfast', 'Larga Estancia',
            'Business Hotel', 'Centro Convenciones', 'Wellness Hotel', 'Spa Hotel', 'Hotel Médico',
            'Hotel Familiar', 'Adults Only', 'Hotel Parejas', 'Hostal Mochilero', 'Pet Friendly',
            'LGBTQ+ Friendly', 'Ejecutivo', 'Estudiantil', 'Deportivo', 'Eventos',
            'Glamping', 'Resort', 'Apartahotel', 'Hostal', 'Posada Turística', 'Lodge',
            'Cabañas', 'Hacienda', 'Motel', 'Parador'
        ])

        # 2. Restaurants (50)
        self.seed_subclass('restaurantes', [
            'A la Carta', 'Buffet', 'Autoservicio', 'Comida Rápida', 'Casual', 'Fine Dining',
            'Corrientazo', 'Take Away', 'Domicilios', 'Food Court',
            'Italiana', 'Mexicana', 'China', 'Japonesa', 'Mediterránea', 'Árabe', 'Francesa',
            'Peruana', 'Típica Colombiana', 'Mariscos',
            'Vegetariano', 'Vegano', 'Saludable', 'Orgánico', 'Sin Gluten', 'Keto', 'Fitness',
            'Macrobiótico', 'Dietético', 'Sostenible',
            'Temático', 'Interactivo', 'Espectáculo', 'Romántico', 'Familiar', 'Pet Friendly',
            'Al Aire Libre', 'Vista Panorámica', 'Ecológico', 'Cultural',
            'Gourmet', 'Bistró', 'Cafetería', 'Trattoria', 'Brasserie', 'Food Truck',
            'Pop-up', 'De Autor', 'Fusión', 'De Mercado'
        ])

        # 3. Bares (50)
        self.seed_subclass('bares', [
            'Tradicional', 'Cócteles', 'Autoservicio', 'Mesa', 'Pub', 'Lounge', 'De Hotel',
            'Restaurante-Bar', 'De Eventos', 'Nocturno',
            'Cervecero', 'Artesanal', 'Wine Bar', 'Premium', 'Autor', 'Whisky', 'Ron', 'Tequila', 'Ginebra', 'Mocktail',
            'Temático', 'Deportivo', 'Musical', 'Karaoke', 'En Vivo', 'Cultural', 'Retro', 'Urbano', 'Alternativo', 'Salsa',
            'Al Aire Libre', 'Rooftop', 'Ecológico', 'Sostenible', 'Pet Friendly', 'VIP', 'Romántico', 'Interactivo', 'Speakeasy', 'Experiencial',
            'Playa', 'Piscina', 'Montaña', 'Rural', 'Móvil', 'Food Truck', 'Flotante', 'Discoteca', 'Turístico', 'Casino'
        ])

        # 4. Discotecas (50)
        self.seed_subclass('discotecas', [
            'EDM', 'Reguetón', 'Crossover', 'Salsa', 'Vallenato', 'Popular', 'Rock', 'Techno', 'House', 'Latina',
            'Temática', 'Retro', 'Urbana', 'Cultural', 'Alternativa', 'Tropical', 'En Vivo', 'DJ Internacional', 'Shows', 'Espectáculo',
            'Juvenil', 'Adultos', 'VIP', 'Turistas', 'LGBTQ+', 'Universitaria', 'Parejas', 'Grupos', 'Inclusiva', 'Privada',
            'Club', 'Lounge', 'Rooftop', 'Al Aire Libre', 'Hotel', 'Bar-Disco', 'Móvil', 'Flotante', 'CC', 'Rural',
            'Lujo', 'Inmersiva', 'Interactiva', 'Tech-LED', 'Silent Disco', 'Ecológica', 'Sostenible', 'After Party', 'Underground', 'Turística'
        ])

        # 5. Agencias (50)
        self.seed_subclass('agencias', [
            'Mayorista', 'Minorista', 'Mayorista-Minorista', 'Operador', 'Emisiva', 'Receptiva', 'Emisiva-Receptiva', 'Consolidadora', 'Intermediaria', 'Eventos',
            'Aventura', 'Ecoturismo', 'Cultural', 'Religioso', 'Gastronómico', 'Comunitario', 'Rural', 'Naturaleza', 'Sostenible', 'Científico',
            'Corporativa', 'Estudiantes', 'Mochileros', 'Lujo', 'Familias', 'Seniors', 'Luna de Miel', 'Accesible', 'LGBTQ+', 'Grupos',
            'OTA', 'Física', 'Híbrida', 'App', 'Social Media', 'Franquicia', 'Independiente', 'Marketplace', 'Virtual', 'AI-Powered',
            'Internacional', 'Nacional', 'Cruceros', 'Médico', 'Deportivo', 'Educativo', 'Wellness', 'MICE', 'Experiencial', 'Medida'
        ])

        # 6. Guías (50)
        self.seed_subclass('guias', [
            'Cultural', 'Histórico', 'Patrimonial', 'Gastronómico', 'Religioso', 'Arqueológico', 'Urbano', 'Rural', 'Comunitario', 'Científico',
            'Ecoturismo', 'Naturaleza', 'Aventura', 'Avistamiento', 'Senderismo', 'Montaña', 'Selva', 'Marino', 'Sostenible', 'Bienestar',
            'Bilingüe', 'Multilingüe', 'Intérprete', 'Animador', 'Educativo', 'Ambiental', 'Primeros Auxilios', 'Facilitador', 'Acompañante', 'Coordinador',
            'Grupos', 'Privado', 'Estudiantes', 'Seniors', 'Familias', 'Extranjeros', 'Accesible', 'Mochileros', 'Lujo', 'Eventos',
            'Local', 'Nacional', 'Freelance', 'Agencia', 'Cruceros', 'Excursiones', 'City Tour', 'Rutas Temáticas', 'Virtual', 'Digital'
        ])

        # 7. Transporte (50)
        self.seed_subclass('transporte', [
            'Terrestre', 'Aéreo', 'Fluvial', 'Marítimo', 'Ferroviario', 'Buses', 'Vans', 'Autos', 'Motos', 'Bicis',
            'Privado', 'Compartido', 'Puerta a Puerta', 'Por Horas', 'Por Rutas', 'Lujo', 'Económico', 'Ejecutivo', 'Todo Incluido', 'Conductor-Guía',
            'Local', 'Regional', 'Nacional', 'Internacional', 'Urbano', 'Intermunicipal', 'Rural', 'Aeropuerto', 'Hotelero', 'Eventos',
            'Grupos', 'Familias', 'Corporativo', 'Escolar', 'Seniors', 'Accesible', 'VIP', 'Mochileros', 'Parejas', 'Cruceristas',
            'Ecológico', 'Aventura 4x4', 'Cultural', 'Gastronómico', 'Religioso', 'Naturaleza', 'City Tour', 'Panorámico', 'Nocturno', 'Temático'
        ])

        # 8. Asociaciones (50)
        self.seed_subclass('agremiaciones', [
            'Prestadores', 'Empresarios', 'Gremial', 'Comunitaria', 'ONG', 'Cooperativa', 'Corporación', 'Fundación', 'Red', 'Clúster',
            'Local', 'Municipal', 'Regional', 'Departamental', 'Nacional', 'Binacional', 'Rural', 'Urbana', 'Destino', 'Corredor',
            'Hoteles', 'Restaurantes', 'Agencias', 'Guías', 'Transportistas', 'Artesanos', 'Operadores', 'Emprendedores', 'Comunitario', 'Mixtos',
            'Ecoturismo', 'Sostenible', 'Naturaleza', 'Cultural', 'Gastronómico', 'Aventura', 'Rural', 'Religioso', 'Bienestar', 'Accesible',
            'Promoción', 'Comercialización', 'Fortalecimiento', 'Capacitación', 'Innovación', 'Desarrollo', 'Planificación', 'Integración', 'Representación', 'Gestión'
        ])

        # 9. Artesanos (50)
        self.seed_subclass('artesanos', [
            'Tejedor', 'Bordador', 'Tallador', 'Alfarero', 'Ceramista', 'Orfebre', 'Joyero', 'Ebanista', 'Carpintero', 'Talabartero',
            'Madera', 'Cerámica', 'Barro', 'Cuero', 'Piedra', 'Metal', 'Vidrio', 'Fibras', 'Papel', 'Textiles',
            'Tradicional', 'Indígena', 'Afro', 'Campesino', 'Ancestral', 'Contemporáneo', 'Urbano', 'Rural', 'Étnico', 'Patrimonial',
            'Decoración', 'Bisutería', 'Joyería', 'Mobiliario', 'Instrumentos', 'Juguetes', 'Utensilios', 'Prendas', 'Accesorios', 'Arte Religioso',
            'Independiente', 'Asociado', 'Emprendedor', 'Exportador', 'Sostenible', 'Ecológico', 'Innovador', 'Tradicional-Comercial', 'Economía Solidaria', 'Turístico'
        ])

        # 10. Delivery (50)
        self.seed_delivery_subclass([
            'Comida Preparada', 'Comida Rápida', 'Mercado', 'Farmacia', 'Bebidas', 'Postres', 'Orgánicos', 'Flores', 'Regalos', 'Mascotas',
            'Gourmet', 'Casera', 'Saludable', 'Internacional', 'Típica', 'Vegetariana', 'Vegana', 'Snacks', 'Panadería', 'Café',
            'Propio', 'Tercerizado', 'Apps', 'Colaborativo', 'Exprés', 'Programado', 'Suscripción', 'Última Milla', 'Cadena Fría', 'Eléctricos',
            'App Móvil', 'Web', 'RRSS', 'WhatsApp', 'Automatizado', 'AI-Powered', 'Real-time Tracking', 'Sin Contacto', 'Pago Digital', 'Omnicanal',
            'Local', 'Urbano', 'Rural', 'Corporativo', 'Eventos', 'Turistas', 'Ecológico', 'Inclusivo', 'Lujo', 'Comunitario'
        ])

        self.stdout.write(self.style.SUCCESS("¡500+ subclasificaciones desplegadas exitosamente!"))

    def seed_subclass(self, cat_slug, labels):
        try:
            cat = CategoriaPrestador.objects.get(slug=cat_slug)
            # Como no tenemos un modelo de 'SubClass' formal aún, usamos Formulario/Pregunta
            # o preparamos para el selector del frontend.
            # Por ahora, guardamos esto en el sistema de Formulario para que el front lo use como opciones.
            form, _ = Formulario.objects.get_or_create(
                nombre=f'Subclasificación - {cat.nombre}',
                defaults={'es_publico': False}
            )
            p, _ = Pregunta.objects.get_or_create(
                formulario=form,
                texto_pregunta='Seleccione su subcategoría',
                tipo_pregunta='SELECCION_UNICA'
            )
            for label in labels:
                OpcionRespuesta.objects.get_or_create(pregunta=p, texto_opcion=label)
        except CategoriaPrestador.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Categoría {cat_slug} no encontrada. Saltando."))

    def seed_delivery_subclass(self, labels):
        # Para Delivery hacemos lo mismo
        form, _ = Formulario.objects.get_or_create(
            nombre='Subclasificación - Delivery',
            defaults={'es_publico': False}
        )
        p, _ = Pregunta.objects.get_or_create(
            formulario=form,
            texto_pregunta='Tipo de Delivery',
            tipo_pregunta='SELECCION_UNICA'
        )
        for label in labels:
            OpcionRespuesta.objects.get_or_create(pregunta=p, texto_opcion=label)
