from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Formulario, Pregunta, OpcionRespuesta, PlantillaVerificacion, ItemVerificacion
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador

class Command(BaseCommand):
    help = 'Crea los formularios de caracterización y las plantillas de verificación final 2026'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando despliegue de formularios institucionales...')

        # 1. Asegurar Categorías
        categorias = [
            ('Agroturismo', 'agroturismo'),
            ('Guías de Turismo', 'guias'),
            ('Artesanos', 'artesanos'),
            ('Consejos Locales', 'consejos-locales'),
            ('Rutas Turísticas', 'rutas'),
            ('Atractivos Naturales', 'atractivos-naturales'),
            ('Operadores Turísticos', 'operadores'),
            ('Agencias de Viajes', 'agencias'),
            ('Alojamiento', 'alojamiento'),
            ('Restaurantes', 'restaurantes'),
            ('Transporte', 'transporte'),
            ('Eventos', 'eventos'),
            ('Agremiaciones', 'agremiaciones'),
            ('Sin RNT', 'sin-rnt'),
        ]

        cat_objs = {}
        for nombre, slug in categorias:
            obj, _ = CategoriaPrestador.objects.get_or_create(nombre=nombre, defaults={'slug': slug})
            cat_objs[slug] = obj

        # 2. Caracterización de Atractivos Naturales
        self.seed_atractivos_naturales()

        # 3. Caracterización de Agroturismo
        self.seed_agroturismo()

        # 4. Caracterización de Eventos (Nuevo Rol)
        self.seed_eventos()

        # 5. Caracterización de Guías
        self.seed_guias()

        # 6. Caracterización de Artesanos
        self.seed_artesanos()

        # 7. Plantilla de Verificación de Cumplimiento (Rural)
        self.seed_compliance_rural()

        self.stdout.write(self.style.SUCCESS('¡Despliegue de formularios completado!'))

    def seed_atractivos_naturales(self):
        form, _ = Formulario.objects.get_or_create(
            nombre='Caracterización de Atractivos Naturales',
            defaults={'titulo': 'CARACTERIZACIÓN DE ATRACTIVOS TURÍSTICOS DE NATURALEZA', 'es_publico': True}
        )
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Nombre Recurso Turístico', tipo_pregunta='TEXTO_CORTO', orden=1)
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Tiempo Inicio de operación', tipo_pregunta='TEXTO_CORTO', orden=2)
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='¿Cuenta con estudios de Capacidad de Carga?', tipo_pregunta='CHECKBOX', orden=3)
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='¿Cuenta con Registro Nacional de Turismo?', tipo_pregunta='CHECKBOX', orden=4)

        p_acceso = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Medio de Transporte de Acceso', tipo_pregunta='SELECCION_MULTIPLE', orden=5)[0]
        for opt in ['Vehículo', 'Lancha', 'Avión', 'Tracción Animal', 'Caminando']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_acceso, texto_opcion=opt)

    def seed_agroturismo(self):
        form, _ = Formulario.objects.get_or_create(
            nombre='Caracterización de Operadores de Agroturismo',
            defaults={'titulo': 'CARACTERIZACIÓN DE OPERADORES DE AGROTURISMO - META', 'es_publico': True}
        )
        p_agri = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Actividades Agrícolas Desarrolladas', tipo_pregunta='SELECCION_MULTIPLE', orden=1)[0]
        for opt in ['Manejo de cultivos', 'Taller de Recolección', 'Visita a la Huerta', 'Hidroponía']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_agri, texto_opcion=opt)

        p_pecu = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Actividades Pecuarias', tipo_pregunta='SELECCION_MULTIPLE', orden=2)[0]
        for opt in ['Cría de Equinos', 'Alimentación Animal', 'Ordeño', 'Trabajo de Llano']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_pecu, texto_opcion=opt)

    def seed_eventos(self):
        form, _ = Formulario.objects.get_or_create(
            nombre='Caracterización de Empresas de Eventos',
            defaults={'titulo': 'CARACTERIZACIÓN EMPRESARIAL DE OPERADORES-EVENTOS, FERIAS Y CONVENCIONES', 'es_publico': True}
        )
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Nombre de la Empresa', tipo_pregunta='TEXTO_CORTO', orden=1)
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Representante Legal', tipo_pregunta='TEXTO_CORTO', orden=2)
        p_serv = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Servicios que ofrece', tipo_pregunta='SELECCION_MULTIPLE', orden=3)[0]
        for opt in ['Organización de Ferias', 'Organización de Eventos', 'Organización de Convenciones', 'Conciertos']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_serv, texto_opcion=opt)

    def seed_guias(self):
        form, _ = Formulario.objects.get_or_create(
            nombre='Caracterización de Guías Turísticos',
            defaults={'titulo': 'CARACTERIZACIÓN DE GUIAS TURISTICOS', 'es_publico': True}
        )
        Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Tarjeta Profesional Número', tipo_pregunta='TEXTO_CORTO', orden=1)
        p_esp = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Especialidad del Guía', tipo_pregunta='SELECCION_MULTIPLE', orden=2)[0]
        for opt in ['Agroturismo', 'Gastronómico', 'Aviturismo', 'Histórico', 'Ecoturismo', 'Aventura']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_esp, texto_opcion=opt)

    def seed_artesanos(self):
        form, _ = Formulario.objects.get_or_create(
            nombre='Caracterización de Artesanos',
            defaults={'titulo': 'CARACTERIZACIÓN DE ARTESANOS', 'es_publico': True}
        )
        p_tipo = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Tipo de Artesanía', tipo_pregunta='SELECCION_UNICA', orden=1)[0]
        for opt in ['Indígena', 'Contemporánea', 'Tradicional popular']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_tipo, texto_opcion=opt)

        p_oficio = Pregunta.objects.get_or_create(formulario=form, texto_pregunta='Oficio Artesanal', tipo_pregunta='SELECCION_MULTIPLE', orden=2)[0]
        for opt in ['Madera', 'Vidrio', 'Tejeduría', 'Cerámica', 'Cuero', 'Metales']:
            OpcionRespuesta.objects.get_or_create(pregunta=p_oficio, texto_opcion=opt)

    def seed_compliance_rural(self):
        plantilla, _ = PlantillaVerificacion.objects.get_or_create(
            nombre='FORMATO DE CARACTERIZACIÓN DE ESTABLECIMIENTOS TURÍSTICOS EN ÁREA RURAL',
            defaults={'descripcion': 'Lista de chequeo para Hoteles y Restaurantes (Zona Rural) - Puerto Gaitán'}
        )

        items = [
            ('Cámara de comercio – Número de matrícula', 'Cámara de comercio', 10),
            ('RUT', 'DIAN', 10),
            ('Permiso de uso de suelo – Licencia de construcción', 'Secretaría de planeación', 10),
            ('Certificado de riesgos de predios', 'Secretaría de planeación', 5),
            ('Permiso de captación de aguas', 'CORMACARENA', 5),
            ('Permiso de vertimientos de aguas residuales', 'CORMACARENA', 5),
            ('Registro nacional de turismo', 'MINCIT', 15),
            ('Concepto bomberil', 'Bomberos', 10),
            ('Pagos de derechos de autor', 'SAYCO y ACINPRO', 5),
            ('Póliza civil extracontractual', 'Empresas de seguros', 10),
            ('Concepto sanitario', 'Secretaría de salud', 10),
            ('Registro de huéspedes', 'Establecimiento', 5),
        ]

        for i, (req, ent, pts) in enumerate(items):
            ItemVerificacion.objects.get_or_create(
                plantilla=plantilla,
                texto_requisito=f"{req} ({ent})",
                defaults={'puntaje': pts, 'orden': i+1, 'es_obligatorio': pts >= 10}
            )
