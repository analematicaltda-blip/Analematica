# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/sitios_turisticos/serializers.py
from rest_framework import serializers
from .models import SitioTuristico, ActividadEnSitio

class ActividadEnSitioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadEnSitio
        fields = [
            'id', 'nombre', 'descripcion', 'duracion_estimada_minutos',
            'precio_adicional', 'requiere_reserva'
        ]

class SitioTuristicoSerializer(serializers.ModelSerializer):
    # Anidar el serializer de actividades para leerlas al obtener un sitio
    actividades = ActividadEnSitioSerializer(many=True, read_only=True)

    class Meta:
        model = SitioTuristico
        fields = [
            'id', 'nombre', 'descripcion_corta', 'descripcion_larga', 'tipo_sitio',
            'ubicacion_latitud', 'ubicacion_longitud', 'direccion_texto',
            'horario_apertura', 'horario_cierre', 'dias_operacion',
            'precio_entrada_adulto', 'precio_entrada_nino', 'activo',
            'actividades' # campo anidado
        ]
        read_only_fields = ('perfil',)
