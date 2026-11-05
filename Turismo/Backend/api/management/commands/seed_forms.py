from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Formulario, Pregunta, OpcionRespuesta, PlantillaVerificacion, ItemVerificacion
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.models import CategoriaPrestador

class Command(BaseCommand):
    help = 'Crea los formularios de caracterización y las plantillas de verificación iniciales'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando la creación de formularios y plantillas...')

        # Crear Categorías de Prestadores de Servicios Turísticos
        categorias_prestadores = [
            'Agencias de Viajes',
            'Alojamientos Turísticos',
            'Gastronomía',
            'Empresas de Transporte Terrestre Automotor',
            'Empresas de Transporte Fluvial',
            'Guías de Turismo',
            'Empresas de Publicidad',
            'Artesanos',
            'Balnearios',
            'Discotecas',
            'Empresas de Recreación',
            'Empresas de Eventos',
            'Empresas de Idiomas',
            'Academias de enseñanza turística',
            'Arrendadores de Vehículos para Turismo'
        ]
        for cat_nombre in categorias_prestadores:
            CategoriaPrestador.objects.get_or_create(nombre=cat_nombre, defaults={'slug': cat_nombre.lower().replace(' ', '-')})
        self.stdout.write(self.style.SUCCESS('Categorías de prestadores de servicios turísticos creadas/verificadas.'))

        # Crear Formularios de Caracterización
        self.crear_formularios_caracterizacion()

        # Crear Plantillas de Verificación
        self.crear_plantillas_verificacion()

        self.stdout.write(self.style.SUCCESS('¡Formularios y plantillas creados exitosamente!'))

    def crear_formularios_caracterizacion(self):
        # Formulario para Agencias de Viajes
        form_agencia, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Agencias de Viajes',
            defaults={
                'titulo': 'Formulario de Caracterización para Agencias de Viajes',
                'descripcion': 'Información detallada sobre agencias de viajes.',
                'categoria': CategoriaPrestador.objects.get(nombre='Agencias de Viajes'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Agencias de Viajes.'))
            Pregunta.objects.create(formulario=form_agencia, texto_pregunta='Tipo de agencia (Mayorista, Minorista, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_agencia, texto_pregunta='Especialización (Ecoturismo, Aventura, Cultural, etc.)', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_agencia, texto_pregunta='Número de empleados', tipo_pregunta='NUMERO', orden=3)
            p_servicios = Pregunta.objects.create(formulario=form_agencia, texto_pregunta='Servicios ofrecidos', tipo_pregunta='SELECCION_MULTIPLE', orden=4)
            OpcionRespuesta.objects.create(pregunta=p_servicios, texto_opcion='Venta de tiquetes aéreos')
            OpcionRespuesta.objects.create(pregunta=p_servicios, texto_opcion='Reservas de hotel')
            OpcionRespuesta.objects.create(pregunta=p_servicios, texto_opcion='Paquetes turísticos completos')
            OpcionRespuesta.objects.create(pregunta=p_servicios, texto_opcion='Alquiler de vehículos')

        # Formulario para Alojamientos Turísticos
        form_alojamiento, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Alojamientos Turísticos',
            defaults={
                'titulo': 'Formulario de Caracterización para Alojamientos Turísticos',
                'descripcion': 'Detalles sobre establecimientos de alojamiento.',
                'categoria': CategoriaPrestador.objects.get(nombre='Alojamientos Turísticos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Alojamientos Turísticos.'))
            Pregunta.objects.create(formulario=form_alojamiento, texto_pregunta='Tipo de alojamiento (Hotel, Hostal, Apartamento, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_alojamiento, texto_pregunta='Número total de habitaciones', tipo_pregunta='NUMERO', es_requerida=True, orden=2)
            Pregunta.objects.create(formulario=form_alojamiento, texto_pregunta='Capacidad total de huéspedes', tipo_pregunta='NUMERO', es_requerida=True, orden=3)
            p_servicios_alojamiento = Pregunta.objects.create(formulario=form_alojamiento, texto_pregunta='Servicios adicionales', tipo_pregunta='SELECCION_MULTIPLE', orden=4)
            OpcionRespuesta.objects.create(pregunta=p_servicios_alojamiento, texto_opcion='Piscina')
            OpcionRespuesta.objects.create(pregunta=p_servicios_alojamiento, texto_opcion='Restaurante')
            OpcionRespuesta.objects.create(pregunta=p_servicios_alojamiento, texto_opcion='Gimnasio')
            OpcionRespuesta.objects.create(pregunta=p_servicios_alojamiento, texto_opcion='Wi-Fi Gratuito')
            Pregunta.objects.create(formulario=form_alojamiento, texto_pregunta='¿Admite mascotas?', tipo_pregunta='SI_NO', orden=5)

        # Formulario para Guías de Turismo
        form_guia, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Guías de Turismo',
            defaults={
                'titulo': 'Formulario de Caracterización para Guías de Turismo',
                'descripcion': 'Información sobre guías de turismo certificados.',
                'categoria': CategoriaPrestador.objects.get(nombre='Guías de Turismo'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Guías de Turismo.'))
            Pregunta.objects.create(formulario=form_guia, texto_pregunta='Número de Tarjeta Profesional de Guía de Turismo', tipo_pregunta='TEXTO_CORTO', es_requerida=True, orden=1)
            p_idiomas = Pregunta.objects.create(formulario=form_guia, texto_pregunta='Idiomas que domina', tipo_pregunta='SELECCION_MULTIPLE', orden=2)
            OpcionRespuesta.objects.create(pregunta=p_idiomas, texto_opcion='Español')
            OpcionRespuesta.objects.create(pregunta=p_idiomas, texto_opcion='Inglés')
            OpcionRespuesta.objects.create(pregunta=p_idiomas, texto_opcion='Francés')
            OpcionRespuesta.objects.create(pregunta=p_idiomas, texto_opcion='Alemán')
            OpcionRespuesta.objects.create(pregunta=p_idiomas, texto_opcion='Portugués')
            Pregunta.objects.create(formulario=form_guia, texto_pregunta='Especialización (Historia, Naturaleza, Aventura, etc.)', tipo_pregunta='TEXTO_LARGO', orden=3)
            Pregunta.objects.create(formulario=form_guia, texto_pregunta='Años de experiencia', tipo_pregunta='NUMERO', orden=4)

        # Formulario para Empresas de Transporte Terrestre
        form_transporte, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Transporte Terrestre',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Transporte Terrestre',
                'descripcion': 'Información sobre empresas de transporte terrestre.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Transporte Terrestre Automotor'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Transporte Terrestre.'))
            Pregunta.objects.create(formulario=form_transporte, texto_pregunta='Tipo de vehículo (Bus, Buseta, Camioneta, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_transporte, texto_pregunta='Capacidad de pasajeros por vehículo', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_transporte, texto_pregunta='Rutas principales', tipo_pregunta='TEXTO_LARGO', orden=3)
            Pregunta.objects.create(formulario=form_transporte, texto_pregunta='¿Ofrece servicios de turismo especializado?', tipo_pregunta='SI_NO', orden=4)

        # Formulario para Empresas de Transporte Fluvial Turístico
        form_fluvial, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas de Transporte Fluvial Turístico',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Transporte Fluvial Turístico',
                'descripcion': 'Información sobre empresas de transporte fluvial turístico.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Transporte Fluvial'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Transporte Fluvial Turístico.'))
            Pregunta.objects.create(formulario=form_fluvial, texto_pregunta='Tipo de embarcación', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_fluvial, texto_pregunta='Capacidad de pasajeros', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_fluvial, texto_pregunta='Rutas o recorridos ofrecidos', tipo_pregunta='TEXTO_LARGO', orden=3)
            Pregunta.objects.create(formulario=form_fluvial, texto_pregunta='¿Cuenta con chalecos salvavidas para todos los pasajeros?', tipo_pregunta='SI_NO', es_requerida=True, orden=4)

        # Formulario para Arrendadores de Vehículos para Turismo
        form_arrendador, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Arrendadores de Vehículos',
            defaults={
                'titulo': 'Formulario de Caracterización para Arrendadores de Vehículos',
                'descripcion': 'Información sobre empresas de alquiler de vehículos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Arrendadores de Vehículos para Turismo'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Arrendadores de Vehículos.'))
            Pregunta.objects.create(formulario=form_arrendador, texto_pregunta='Tipos de vehículos disponibles (ej. sedan, camioneta, van)', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_arrendador, texto_pregunta='Número total de vehículos en la flota', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_arrendador, texto_pregunta='¿Ofrece seguro a todo riesgo?', tipo_pregunta='SI_NO', es_requerida=True, orden=3)
            Pregunta.objects.create(formulario=form_arrendador, texto_pregunta='Requisitos para el alquiler (edad mínima, licencia, etc.)', tipo_pregunta='TEXTO_LARGO', orden=4)

        # Formulario para Viviendas Turísticas y Otros Tipos de Hospedaje Turístico
        form_vivienda, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Viviendas Turísticas',
            defaults={
                'titulo': 'Formulario de Caracterización para Viviendas Turísticas y Otros Tipos de Hospedaje Turístico',
                'descripcion': 'Información sobre viviendas turísticas y otros tipos de hospedaje.',
                'categoria': CategoriaPrestador.objects.get(nombre='Viviendas Turísticas y Otros Tipos de Hospedaje Turístico'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Viviendas Turísticas.'))
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Tipo de Vivienda (ej. Apartamento, Casa, Finca)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Número de Registro Nacional de Turismo (RNT)', tipo_pregunta='TEXTO_CORTO', es_requerida=True, orden=2)
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Capacidad máxima de huéspedes', tipo_pregunta='NUMERO', es_requerida=True, orden=3)
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Número de habitaciones', tipo_pregunta='NUMERO', es_requerida=True, orden=4)
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Número de baños', tipo_pregunta='NUMERO', es_requerida=True, orden=5)
            p_servicios_vivienda = Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='Servicios ofrecidos', tipo_pregunta='SELECCION_MULTIPLE', orden=6)
            OpcionRespuesta.objects.create(pregunta=p_servicios_vivienda, texto_opcion='Piscina')
            OpcionRespuesta.objects.create(pregunta=p_servicios_vivienda, texto_opcion='Wi-Fi')
            OpcionRespuesta.objects.create(pregunta=p_servicios_vivienda, texto_opcion='Cocina equipada')
            OpcionRespuesta.objects.create(pregunta=p_servicios_vivienda, texto_opcion='Aire acondicionado')
            OpcionRespuesta.objects.create(pregunta=p_servicios_vivienda, texto_opcion='Parqueadero')
            p_tipo_alojamiento = Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='¿El alojamiento es exclusivo para los huéspedes o es compartido con los anfitriones?', tipo_pregunta='SELECCION_UNICA', orden=7)
            OpcionRespuesta.objects.create(pregunta=p_tipo_alojamiento, texto_opcion='Exclusivo para huéspedes')
            OpcionRespuesta.objects.create(pregunta=p_tipo_alojamiento, texto_opcion='Compartido con anfitriones')
            Pregunta.objects.create(formulario=form_vivienda, texto_pregunta='¿Admite mascotas?', tipo_pregunta='SI_NO', orden=8)

        # Formulario para Establecimientos de Gastronomía y Bares Turísticos
        form_gastro, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Establecimientos de Gastronomía y Bares',
            defaults={
                'titulo': 'Formulario de Caracterización para Establecimientos de Gastronomía y Bares Turísticos',
                'descripcion': 'Información sobre restaurantes, bares y similares.',
                'categoria': CategoriaPrestador.objects.get(nombre='Gastronomía'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Establecimientos de Gastronomía y Bares.'))
            Pregunta.objects.create(formulario=form_gastro, texto_pregunta='Tipo de establecimiento (Restaurante, Bar, Café, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_gastro, texto_pregunta='Especialidad gastronómica', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_gastro, texto_pregunta='Capacidad (número de mesas/asientos)', tipo_pregunta='NUMERO', orden=3)
            p_ambiente = Pregunta.objects.create(formulario=form_gastro, texto_pregunta='Ambiente', tipo_pregunta='SELECCION_MULTIPLE', orden=4)
            OpcionRespuesta.objects.create(pregunta=p_ambiente, texto_opcion='Familiar')
            OpcionRespuesta.objects.create(pregunta=p_ambiente, texto_opcion='Romántico')
            OpcionRespuesta.objects.create(pregunta=p_ambiente, texto_opcion='Negocios')
            OpcionRespuesta.objects.create(pregunta=p_ambiente, texto_opcion='Música en vivo')
            Pregunta.objects.create(formulario=form_gastro, texto_pregunta='¿Ofrece opciones vegetarianas/veganas?', tipo_pregunta='SI_NO', orden=5)

        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Publicidad.'))
            Pregunta.objects.create(formulario=form_publicidad, texto_pregunta='Tipo de plataforma (Sitio web, App, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_publicidad, texto_pregunta='Alcance de la plataforma (Local, Nacional, Internacional)', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_publicidad, texto_pregunta='Número de usuarios registrados', tipo_pregunta='NUMERO', orden=3)

        # Formulario para Empresas Organizadoras de Congresos, Ferias y Convenciones
        form_eventos, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas Organizadoras de Eventos',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas Organizadoras de Congresos, Ferias y Convenciones',
                'descripcion': 'Información sobre empresas organizadoras de eventos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Eventos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas Organizadoras de Eventos.'))
            Pregunta.objects.create(formulario=form_eventos, texto_pregunta='Tipos de eventos que organiza (Congresos, Convenciones, Ferias, etc.)', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_eventos, texto_pregunta='Capacidad máxima de asistentes en eventos gestionados', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_eventos, texto_pregunta='Servicios ofrecidos (logística, catering, etc.)', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Oficinas de Representación Turística
        form_rep, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Oficinas de Representación Turística',
            defaults={
                'titulo': 'Formulario de Caracterización para Oficinas de Representación Turística',
                'descripcion': 'Información sobre oficinas de representación turística.',
                'categoria': CategoriaPrestador.objects.get(nombre='Oficinas de Representación Turística'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Oficinas de Representación Turística.'))
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Tipo de representación (Hotel, Aerolínea, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Mercados principales a los que se dirige', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Número de empleados', tipo_pregunta='NUMERO', orden=3)

        # Formulario para Operadores Profesionales de Congresos, Ferias y Convenciones
        form_op_eventos, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Operadores Profesionales de Congresos, Ferias y Convenciones',
            defaults={
                'titulo': 'Formulario de Caracterización para Operadores Profesionales de Congresos, Ferias y Convenciones',
                'descripcion': 'Información sobre operadores profesionales de eventos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Operadores Profesionales de Congresos, Ferias y Convenciones'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Operadores Profesionales de Congresos, Ferias y Convenciones.'))
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Tipo de eventos que opera', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Capacidad logística', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Certificaciones en organización de eventos', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Empresas de Turismo de Naturaleza o Aventura
        form_aventura, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas de Turismo de Naturaleza o Aventura',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Turismo de Naturaleza o Aventura',
                'descripcion': 'Información sobre empresas de turismo de naturaleza o aventura.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Turismo de Naturaleza o Aventura'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Turismo de Naturaleza o Aventura.'))
            p_actividades = Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Actividades que ofrece', tipo_pregunta='SELECCION_MULTIPLE', orden=1)
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Senderismo')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Canopy')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Rafting')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Buceo')
            Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Niveles de dificultad de las actividades', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Certificaciones de seguridad', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Parques Temáticos
        form_parque, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Parques Temáticos',
            defaults={
                'titulo': 'Formulario de Caracterización para Parques Temáticos',
                'descripcion': 'Información sobre parques temáticos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Parques Temáticos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Parques Temáticos.'))
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Temática principal del parque', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Capacidad máxima de visitantes por día', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Atracciones principales', tipo_pregunta='TEXTO_LARGO', orden=3)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Servicios adicionales (restaurantes, tiendas, etc.)', tipo_pregunta='TEXTO_LARGO', orden=4)

        # Formulario para Concesionarios de Servicios Turísticos en Parques
        form_concesionario, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Concesionarios de Servicios Turísticos en Parques',
            defaults={
                'titulo': 'Formulario de Caracterización para Concesionarios de Servicios Turísticos en Parques',
                'descripcion': 'Información sobre concesionarios de servicios turísticos en parques.',
                'categoria': CategoriaPrestador.objects.get(nombre='Concesionarios de Servicios Turísticos en Parques'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Concesionarios de Servicios Turísticos en Parques.'))
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Parque en el que opera', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Tipo de servicio (alimentación, souvenirs, etc.)', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Años de operación de la concesión', tipo_pregunta='NUMERO', orden=3)

        # Formulario para Artesanos
        form_artesano, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Artesanos',
            defaults={
                'titulo': 'Formulario de Caracterización para Artesanos',
                'descripcion': 'Información sobre artesanos y sus productos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Artesanos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Artesanos.'))
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Tipo de artesanía', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Materiales utilizados', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Técnicas de producción', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Balnearios
        form_balneario, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Balnearios',
            defaults={
                'titulo': 'Formulario de Caracterización para Balnearios',
                'descripcion': 'Información sobre balnearios.',
                'categoria': CategoriaPrestador.objects.get(nombre='Balnearios'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Balnearios.'))
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Tipo de balneario (piscina, río, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Capacidad de personas', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Servicios adicionales (restaurante, vestuarios, etc.)', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Discotecas
        form_discoteca, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Discotecas',
            defaults={
                'titulo': 'Formulario de Caracterización para Discotecas',
                'descripcion': 'Información sobre discotecas y bares.',
                'categoria': CategoriaPrestador.objects.get(nombre='Discotecas'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Discotecas.'))
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Tipo de música principal', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Capacidad del local', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Días de apertura', tipo_pregunta='TEXTO_CORTO', orden=3)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='¿Ofrece servicio de bar?', tipo_pregunta='SI_NO', orden=4)

        # Formulario para Empresas de Recreación
        form_recreacion, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas de Recreación',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Recreación',
                'descripcion': 'Información sobre empresas de recreación.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Recreación'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Recreación.'))
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='Tipos de actividades recreativas ofrecidas', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='Edades a las que se dirige', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='¿Requiere reserva previa?', tipo_pregunta='SI_NO', orden=3)

        # Formulario para Empresas de Idiomas
        form_idiomas, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Academias de Idiomas',
            defaults={
                'titulo': 'Formulario de Caracterización para Academias de Idiomas',
                'descripcion': 'Información sobre academias de idiomas.',
                'categoria': CategoriaPrestador.objects.get(nombre='Academias de enseñanza turística'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Academias de Idiomas.'))
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='Idiomas que se enseñan', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='Niveles de enseñanza (básico, intermedio, avanzado)', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='¿Ofrece cursos para turistas?', tipo_pregunta='SI_NO', orden=3)

        self.stdout.write(self.style.SUCCESS('Formularios de caracterización creados/verificados.'))

    def crear_plantillas_verificacion(self):
        # Plantilla para Agencias de Viajes
        cat_agencia = CategoriaPrestador.objects.get(nombre='Agencias de Viajes')
        plantilla_agencia, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Agencias de Viajes',
            defaults={'categoria_prestador': cat_agencia, 'descripcion': 'Requisitos para agencias de viajes.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Agencias de Viajes.'))
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=25, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Cámara de Comercio renovada', puntaje=25, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Pólizas de seguro de responsabilidad civil', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Certificados de calidad turística (si aplica)', puntaje=15, es_obligatorio=False, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Contratos con proveedores de servicios', puntaje=15, es_obligatorio=False, orden=5)

        # Plantilla para Alojamientos Turísticos
        cat_alojamiento = CategoriaPrestador.objects.get(nombre='Alojamientos Turísticos')
        plantilla_alojamiento, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Alojamientos Turísticos',
            defaults={'categoria_prestador': cat_alojamiento, 'descripcion': 'Requisitos para alojamientos turísticos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Alojamientos Turísticos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=20, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Cámara de Comercio renovada', puntaje=20, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Concepto de uso de suelo', puntaje=15, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Certificado de seguridad de bomberos', puntaje=15, es_obligatorio=True, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Plan de manejo de residuos', puntaje=10, es_obligatorio=False, orden=5)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Protocolos de bioseguridad', puntaje=10, es_obligatorio=True, orden=6)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Accesibilidad para personas con discapacidad', puntaje=10, es_obligatorio=False, orden=7)

            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Accesibilidad para personas con discapacidad', puntaje=10, es_obligatorio=False, orden=7)

        # Plantilla para Establecimientos de Gastronomía y Bares Turísticos
        cat_gastro = CategoriaPrestador.objects.get(nombre='Gastronomía')
        plantilla_gastro, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Establecimientos Gastronómicos',
            defaults={'categoria_prestador': cat_gastro, 'descripcion': 'Requisitos para establecimientos de gastronomía y bares.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Gastronomía.'))
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=20, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Cámara de Comercio renovada', puntaje=20, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Concepto Sanitario Favorable', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Certificado de seguridad de bomberos', puntaje=15, es_obligatorio=True, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Plan de manejo de residuos sólidos y líquidos', puntaje=15, es_obligatorio=False, orden=5)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Menú disponible en al menos un segundo idioma', puntaje=10, es_obligatorio=False, orden=6)

        # Formulario para Oficinas de Representación Turística
        form_rep, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Oficinas de Representación Turística',
            defaults={
                'titulo': 'Formulario de Caracterización para Oficinas de Representación Turística',
                'descripcion': 'Información sobre oficinas de representación turística.',
                'categoria': CategoriaPrestador.objects.get(nombre='Oficinas de Representación Turística'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Oficinas de Representación Turística.'))
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Tipo de representación (Hotel, Aerolínea, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Mercados principales a los que se dirige', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_rep, texto_pregunta='Número de empleados', tipo_pregunta='NUMERO', orden=3)

        # Formulario para Operadores Profesionales de Congresos, Ferias y Convenciones
        form_op_eventos, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Operadores Profesionales de Congresos, Ferias y Convenciones',
            defaults={
                'titulo': 'Formulario de Caracterización para Operadores Profesionales de Congresos, Ferias y Convenciones',
                'descripcion': 'Información sobre operadores profesionales de eventos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Operadores Profesionales de Congresos, Ferias y Convenciones'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Operadores Profesionales de Congresos, Ferias y Convenciones.'))
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Tipo de eventos que opera', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Capacidad logística', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_op_eventos, texto_pregunta='Certificaciones en organización de eventos', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Empresas de Turismo de Naturaleza o Aventura
        form_aventura, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas de Turismo de Naturaleza o Aventura',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Turismo de Naturaleza o Aventura',
                'descripcion': 'Información sobre empresas de turismo de naturaleza o aventura.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Turismo de Naturaleza o Aventura'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Turismo de Naturaleza o Aventura.'))
            p_actividades = Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Actividades que ofrece', tipo_pregunta='SELECCION_MULTIPLE', orden=1)
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Senderismo')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Canopy')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Rafting')
            OpcionRespuesta.objects.create(pregunta=p_actividades, texto_opcion='Buceo')
            Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Niveles de dificultad de las actividades', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_aventura, texto_pregunta='Certificaciones de seguridad', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Parques Temáticos
        form_parque, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Parques Temáticos',
            defaults={
                'titulo': 'Formulario de Caracterización para Parques Temáticos',
                'descripcion': 'Información sobre parques temáticos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Parques Temáticos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Parques Temáticos.'))
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Temática principal del parque', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Capacidad máxima de visitantes por día', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Atracciones principales', tipo_pregunta='TEXTO_LARGO', orden=3)
            Pregunta.objects.create(formulario=form_parque, texto_pregunta='Servicios adicionales (restaurantes, tiendas, etc.)', tipo_pregunta='TEXTO_LARGO', orden=4)

        # Formulario para Concesionarios de Servicios Turísticos en Parques
        form_concesionario, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Concesionarios de Servicios Turísticos en Parques',
            defaults={
                'titulo': 'Formulario de Caracterización para Concesionarios de Servicios Turísticos en Parques',
                'descripcion': 'Información sobre concesionarios de servicios turísticos en parques.',
                'categoria': CategoriaPrestador.objects.get(nombre='Concesionarios de Servicios Turísticos en Parques'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Concesionarios de Servicios Turísticos en Parques.'))
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Parque en el que opera', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Tipo de servicio (alimentación, souvenirs, etc.)', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_concesionario, texto_pregunta='Años de operación de la concesión', tipo_pregunta='NUMERO', orden=3)

        # Formulario para Artesanos
        form_artesano, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Artesanos',
            defaults={
                'titulo': 'Formulario de Caracterización para Artesanos',
                'descripcion': 'Información sobre artesanos y sus productos.',
                'categoria': CategoriaPrestador.objects.get(nombre='Artesanos'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Artesanos.'))
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Tipo de artesanía', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Materiales utilizados', tipo_pregunta='TEXTO_LARGO', orden=2)
            Pregunta.objects.create(formulario=form_artesano, texto_pregunta='Técnicas de producción', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Balnearios
        form_balneario, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Balnearios',
            defaults={
                'titulo': 'Formulario de Caracterización para Balnearios',
                'descripcion': 'Información sobre balnearios.',
                'categoria': CategoriaPrestador.objects.get(nombre='Balnearios'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Balnearios.'))
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Tipo de balneario (piscina, río, etc.)', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Capacidad de personas', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_balneario, texto_pregunta='Servicios adicionales (restaurante, vestuarios, etc.)', tipo_pregunta='TEXTO_LARGO', orden=3)

        # Formulario para Discotecas
        form_discoteca, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Discotecas',
            defaults={
                'titulo': 'Formulario de Caracterización para Discotecas',
                'descripcion': 'Información sobre discotecas y bares.',
                'categoria': CategoriaPrestador.objects.get(nombre='Discotecas'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Discotecas.'))
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Tipo de música principal', tipo_pregunta='TEXTO_CORTO', orden=1)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Capacidad del local', tipo_pregunta='NUMERO', orden=2)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='Días de apertura', tipo_pregunta='TEXTO_CORTO', orden=3)
            Pregunta.objects.create(formulario=form_discoteca, texto_pregunta='¿Ofrece servicio de bar?', tipo_pregunta='SI_NO', orden=4)

        # Formulario para Empresas de Recreación
        form_recreacion, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Empresas de Recreación',
            defaults={
                'titulo': 'Formulario de Caracterización para Empresas de Recreación',
                'descripcion': 'Información sobre empresas de recreación.',
                'categoria': CategoriaPrestador.objects.get(nombre='Empresas de Recreación'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Empresas de Recreación.'))
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='Tipos de actividades recreativas ofrecidas', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='Edades a las que se dirige', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_recreacion, texto_pregunta='¿Requiere reserva previa?', tipo_pregunta='SI_NO', orden=3)

        # Formulario para Empresas de Idiomas
        form_idiomas, created = Formulario.objects.update_or_create(
            nombre='Caracterización de Academias de Idiomas',
            defaults={
                'titulo': 'Formulario de Caracterización para Academias de Idiomas',
                'descripcion': 'Información sobre academias de idiomas.',
                'categoria': CategoriaPrestador.objects.get(nombre='Academias de enseñanza turística'),
                'es_publico': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creado formulario para Academias de Idiomas.'))
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='Idiomas que se enseñan', tipo_pregunta='TEXTO_LARGO', orden=1)
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='Niveles de enseñanza (básico, intermedio, avanzado)', tipo_pregunta='TEXTO_CORTO', orden=2)
            Pregunta.objects.create(formulario=form_idiomas, texto_pregunta='¿Ofrece cursos para turistas?', tipo_pregunta='SI_NO', orden=3)
        self.stdout.write(self.style.SUCCESS('Formularios de caracterización creados/verificados.'))

    def crear_plantillas_verificacion(self):
        # Plantilla para Agencias de Viajes
        cat_agencia = CategoriaPrestador.objects.get(nombre='Agencias de Viajes')
        plantilla_agencia, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Agencias de Viajes',
            defaults={'categoria_prestador': cat_agencia, 'descripcion': 'Requisitos para agencias de viajes.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Agencias de Viajes.'))
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=25, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Cámara de Comercio renovada', puntaje=25, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Pólizas de seguro de responsabilidad civil', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Certificados de calidad turística (si aplica)', puntaje=15, es_obligatorio=False, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_agencia, texto_requisito='Contratos con proveedores de servicios', puntaje=15, es_obligatorio=False, orden=5)

        # Plantilla para Alojamientos Turísticos
        cat_alojamiento = CategoriaPrestador.objects.get(nombre='Alojamientos Turísticos')
        plantilla_alojamiento, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Alojamientos Turísticos',
            defaults={'categoria_prestador': cat_alojamiento, 'descripcion': 'Requisitos para alojamientos turísticos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Alojamientos Turísticos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=20, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Cámara de Comercio renovada', puntaje=20, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Concepto de uso de suelo', puntaje=15, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Certificado de seguridad de bomberos', puntaje=15, es_obligatorio=True, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Plan de manejo de residuos', puntaje=10, es_obligatorio=False, orden=5)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Protocolos de bioseguridad', puntaje=10, es_obligatorio=True, orden=6)
            ItemVerificacion.objects.create(plantilla=plantilla_alojamiento, texto_requisito='Accesibilidad para personas con discapacidad', puntaje=10, es_obligatorio=False, orden=7)
        
        # Plantilla para Establecimientos de Gastronomía y Bares Turísticos
        cat_gastro = CategoriaPrestador.objects.get(nombre='Gastronomía')
        plantilla_gastro, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Establecimientos Gastronómicos',
            defaults={'categoria_prestador': cat_gastro, 'descripcion': 'Requisitos para establecimientos de gastronomía y bares.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Gastronomía.'))
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=20, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Cámara de Comercio renovada', puntaje=20, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Concepto Sanitario Favorable', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Certificado de seguridad de bomberos', puntaje=15, es_obligatorio=True, orden=4)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Plan de manejo de residuos sólidos y líquidos', puntaje=15, es_obligatorio=False, orden=5)
            ItemVerificacion.objects.create(plantilla=plantilla_gastro, texto_requisito='Menú disponible en al menos un segundo idioma', puntaje=10, es_obligatorio=False, orden=6)

        # Plantilla para Guías de Turismo
        cat_guia = CategoriaPrestador.objects.get(nombre='Guías de Turismo')
        plantilla_guia, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Guías de Turismo',
            defaults={'categoria_prestador': cat_guia, 'descripcion': 'Requisitos para guías de turismo.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Guías de Turismo.'))
            ItemVerificacion.objects.create(plantilla=plantilla_guia, texto_requisito='Tarjeta Profesional de Guía de Turismo vigente', puntaje=50, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_guia, texto_requisito='Certificación en primeros auxilios', puntaje=25, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_guia, texto_requisito='Dominio de un segundo idioma (certificado)', puntaje=25, es_obligatorio=False, orden=3)

        # Plantilla para Empresas de Transporte Fluvial
        cat_fluvial = CategoriaPrestador.objects.get(nombre='Empresas de Transporte Fluvial')
        plantilla_fluvial, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Transporte Fluvial',
            defaults={'categoria_prestador': cat_fluvial, 'descripcion': 'Requisitos para transporte fluvial.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Transporte Fluvial.'))
            ItemVerificacion.objects.create(plantilla=plantilla_fluvial, texto_requisito='Permiso de operación de la autoridad marítima', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_fluvial, texto_requisito='Certificados de seguridad de las embarcaciones', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_fluvial, texto_requisito='Chalecos salvavidas y equipo de seguridad a bordo', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_fluvial, texto_requisito='Capacitación de la tripulación', puntaje=20, es_obligatorio=False, orden=4)

        # Plantilla para Arrendadores de Vehículos para Turismo
        cat_arrendador = CategoriaPrestador.objects.get(nombre='Arrendadores de Vehículos para Turismo')
        plantilla_arrendador, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Arrendadores de Vehículos',
            defaults={'categoria_prestador': cat_arrendador, 'descripcion': 'Requisitos para arrendadores de vehículos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Arrendadores de Vehículos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_arrendador, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_arrendador, texto_requisito='Pólizas de seguro para los vehículos', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_arrendador, texto_requisito='Contrato de arrendamiento claro y visible', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_arrendador, texto_requisito='Mantenimiento preventivo de la flota', puntaje=20, es_obligatorio=False, orden=4)

        # Plantilla para Viviendas Turísticas y Otros Tipos de Hospedaje Turístico
        cat_vivienda = CategoriaPrestador.objects.get(nombre='Viviendas Turísticas y Otros Tipos de Hospedaje Turístico')
        plantilla_vivienda, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Viviendas Turísticas',
            defaults={'categoria_prestador': cat_vivienda, 'descripcion': 'Requisitos para viviendas turísticas.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Viviendas Turísticas.'))
            ItemVerificacion.objects.create(plantilla=plantilla_vivienda, texto_requisito='Registro Nacional de Turismo (RNT) vigente', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_vivienda, texto_requisito='Condiciones de seguridad y salubridad adecuadas', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_vivienda, texto_requisito='Información clara sobre servicios y tarifas', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_vivienda, texto_requisito='Publicidad acorde a la realidad del inmueble', puntaje=20, es_obligatorio=False, orden=4)

        # Plantilla para Empresas de Publicidad u Operadores de Plataformas Tecnológicas
        cat_publicidad = CategoriaPrestador.objects.get(nombre='Empresas de Publicidad')
        plantilla_publicidad, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Empresas de Publicidad',
            defaults={'categoria_prestador': cat_publicidad, 'descripcion': 'Requisitos para empresas de publicidad.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Empresas de Publicidad.'))
            ItemVerificacion.objects.create(plantilla=plantilla_publicidad, texto_requisito='Cumplimiento de normativas de publicidad y consumo', puntaje=50, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_publicidad, texto_requisito='Protección de datos de usuarios', puntaje=50, es_obligatorio=True, orden=2)

        # Plantilla para Empresas Organizadoras de Congresos, Ferias y Convenciones
        cat_eventos = CategoriaPrestador.objects.get(nombre='Empresas de Eventos')
        plantilla_eventos, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Empresas de Eventos',
            defaults={'categoria_prestador': cat_eventos, 'descripcion': 'Requisitos para empresas de eventos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Empresas de Eventos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_eventos, texto_requisito='Permisos y licencias para eventos', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_eventos, texto_requisito='Planes de contingencia y seguridad', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_eventos, texto_requisito='Seguro de responsabilidad civil para eventos', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_eventos, texto_requisito='Experiencia comprobable en organización de eventos', puntaje=20, es_obligatorio=False, orden=4)

        # Plantilla para Oficinas de Representación Turística
        cat_representacion = CategoriaPrestador.objects.get(nombre='Oficinas de Representación Turística')
        plantilla_representacion, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Oficinas de Representación Turística',
            defaults={'categoria_prestador': cat_representacion, 'descripcion': 'Requisitos para oficinas de representación turística.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Oficinas de Representación Turística.'))
            ItemVerificacion.objects.create(plantilla=plantilla_representacion, texto_requisito='Registro Mercantil vigente', puntaje=50, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_representacion, texto_requisito='Contratos de representación con empresas turísticas', puntaje=50, es_obligatorio=True, orden=2)

        # Plantilla para Operadores Profesionales de Congresos, Ferias y Convenciones
        cat_op_eventos = CategoriaPrestador.objects.get(nombre='Operadores Profesionales de Congresos, Ferias y Convenciones')
        plantilla_op_eventos, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Operadores Profesionales de Congresos',
            defaults={'categoria_prestador': cat_op_eventos, 'descripcion': 'Requisitos para operadores de congresos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Operadores Profesionales de Congresos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_op_eventos, texto_requisito='Experiencia demostrable en la organización de congresos', puntaje=40, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_op_eventos, texto_requisito='Referencias de clientes anteriores', puntaje=30, es_obligatorio=False, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_op_eventos, texto_requisito='Capacidad de gestión de inscripciones y logística', puntaje=30, es_obligatorio=True, orden=3)

        # Plantilla para Empresas de Turismo de Naturaleza o Aventura
        cat_aventura = CategoriaPrestador.objects.get(nombre='Empresas de Turismo de Naturaleza o Aventura')
        plantilla_aventura, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Turismo de Naturaleza o Aventura',
            defaults={'categoria_prestador': cat_aventura, 'descripcion': 'Requisitos para empresas de turismo de naturaleza o aventura.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Turismo de Naturaleza o Aventura.'))
            ItemVerificacion.objects.create(plantilla=plantilla_aventura, texto_requisito='Guías certificados en la actividad específica', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_aventura, texto_requisito='Protocolos de seguridad y gestión de riesgos', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_aventura, texto_requisito='Pólizas de seguro de accidentes', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_aventura, texto_requisito='Permisos para operar en áreas protegidas (si aplica)', puntaje=20, es_obligatorio=False, orden=4)

        # Plantilla para Parques Temáticos
        cat_parque = CategoriaPrestador.objects.get(nombre='Parques Temáticos')
        plantilla_parque, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Parques Temáticos',
            defaults={'categoria_prestador': cat_parque, 'descripcion': 'Requisitos para parques temáticos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Parques Temáticos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_parque, texto_requisito='Plan de mantenimiento de atracciones', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_parque, texto_requisito='Plan de emergencias y evacuación', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_parque, texto_requisito='Personal capacitado en primeros auxilios', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_parque, texto_requisito='Señalización clara y visible', puntaje=20, es_obligatorio=True, orden=4)

        # Plantilla para Concesionarios de Servicios Turísticos en Parques
        cat_concesionario = CategoriaPrestador.objects.get(nombre='Concesionarios de Servicios Turísticos en Parques')
        plantilla_concesionario, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Concesionarios en Parques',
            defaults={'categoria_prestador': cat_concesionario, 'descripcion': 'Requisitos para concesionarios en parques.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Concesionarios en Parques.'))
            ItemVerificacion.objects.create(plantilla=plantilla_concesionario, texto_requisito='Contrato de concesión vigente', puntaje=40, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_concesionario, texto_requisito='Cumplimiento de las normas del parque', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_concesionario, texto_requisito='Calidad del servicio ofrecido', puntaje=30, es_obligatorio=False, orden=3)

        # Plantilla para Artesanos
        cat_artesano = CategoriaPrestador.objects.get(nombre='Artesanos')
        plantilla_artesano, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Artesanos',
            defaults={'categoria_prestador': cat_artesano, 'descripcion': 'Requisitos para artesanos.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Artesanos.'))
            ItemVerificacion.objects.create(plantilla=plantilla_artesano, texto_requisito='Registro Único de Artesanos (RUA)', puntaje=50, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_artesano, texto_requisito='Certificado de origen de los materiales', puntaje=25, es_obligatorio=False, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_artesano, texto_requisito='Participación en ferias artesanales reconocidas', puntaje=25, es_obligatorio=False, orden=3)

        # Plantilla para Balnearios
        cat_balneario = CategoriaPrestador.objects.get(nombre='Balnearios')
        plantilla_balneario, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Balnearios',
            defaults={'categoria_prestador': cat_balneario, 'descripcion': 'Requisitos para balnearios.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Balnearios.'))
            ItemVerificacion.objects.create(plantilla=plantilla_balneario, texto_requisito='Calidad del agua certificada', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_balneario, texto_requisito='Servicios de salvavidas y primeros auxilios', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_balneario, texto_requisito='Instalaciones sanitarias adecuadas', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_balneario, texto_requisito='Señalización de profundidad y zonas de riesgo', puntaje=20, es_obligatorio=True, orden=4)

        # Plantilla para Discotecas
        cat_discoteca = CategoriaPrestador.objects.get(nombre='Discotecas')
        plantilla_discoteca, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Discotecas',
            defaults={'categoria_prestador': cat_discoteca, 'descripcion': 'Requisitos para discotecas.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Discotecas.'))
            ItemVerificacion.objects.create(plantilla=plantilla_discoteca, texto_requisito='Licencia de funcionamiento vigente', puntaje=30, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_discoteca, texto_requisito='Plan de evacuación y seguridad contra incendios', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_discoteca, texto_requisito='Control de aforo', puntaje=20, es_obligatorio=True, orden=3)
            ItemVerificacion.objects.create(plantilla=plantilla_discoteca, texto_requisito='Personal de seguridad capacitado', puntaje=20, es_obligatorio=True, orden=4)

        # Plantilla para Empresas de Recreación
        cat_recreacion = CategoriaPrestador.objects.get(nombre='Empresas de Recreación')
        plantilla_recreacion, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Empresas de Recreación',
            defaults={'categoria_prestador': cat_recreacion, 'descripcion': 'Requisitos para empresas de recreación.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Empresas de Recreación.'))
            ItemVerificacion.objects.create(plantilla=plantilla_recreacion, texto_requisito='Póliza de responsabilidad civil', puntaje=40, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_recreacion, texto_requisito='Protocolos de seguridad para cada actividad', puntaje=40, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_recreacion, texto_requisito='Personal capacitado y certificado', puntaje=20, es_obligatorio=True, orden=3)

        # Plantilla para Empresas de Idiomas
        cat_idiomas = CategoriaPrestador.objects.get(nombre='Empresas de Idiomas')
        plantilla_idiomas, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Academias de Idiomas',
            defaults={'categoria_prestador': cat_idiomas, 'descripcion': 'Requisitos para academias de idiomas.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Academias de Idiomas.'))
            ItemVerificacion.objects.create(plantilla=plantilla_idiomas, texto_requisito='Licencia de funcionamiento', puntaje=40, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_idiomas, texto_requisito='Certificación de los docentes', puntaje=40, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_idiomas, texto_requisito='Material didáctico adecuado', puntaje=20, es_obligatorio=False, orden=3)

        # Plantilla para Academias de enseñanza turística
        cat_academia = CategoriaPrestador.objects.get(nombre='Academias de enseñanza turística')
        plantilla_academia, created = PlantillaVerificacion.objects.update_or_create(
            nombre='Verificación de Academias de Enseñanza Turística',
            defaults={'categoria_prestador': cat_academia, 'descripcion': 'Requisitos para academias de enseñanza turística.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Creada plantilla de verificación para Academias de Enseñanza Turística.'))
            ItemVerificacion.objects.create(plantilla=plantilla_academia, texto_requisito='Registro Calificado del Ministerio de Educación', puntaje=50, es_obligatorio=True, orden=1)
            ItemVerificacion.objects.create(plantilla=plantilla_academia, texto_requisito='Plan de estudios aprobado', puntaje=30, es_obligatorio=True, orden=2)
            ItemVerificacion.objects.create(plantilla=plantilla_academia, texto_requisito='Infraestructura adecuada para la enseñanza', puntaje=20, es_obligatorio=True, orden=3)

        self.stdout.write(self.style.SUCCESS('Plantillas de verificación creadas/verificadas.'))
 