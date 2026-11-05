from rest_framework import serializers
from .models import Valoracion
from api.serializers import CustomUserSerializer # Para mostrar info del turista

class ValoracionSerializer(serializers.ModelSerializer):
    # Mostramos info del turista de forma anidada y de solo lectura
    turista = CustomUserSerializer(read_only=True)

    class Meta:
        model = Valoracion
        fields = (
            'id', 'producto', 'turista', 'puntuacion', 'comentario',
            'fecha_creacion', 'respuesta_del_prestador', 'fecha_respuesta'
        )
        read_only_fields = ('perfil_prestador', 'turista', 'fecha_creacion', 'fecha_respuesta')

class RespuestaPrestadorSerializer(serializers.ModelSerializer):
    """
    Serializador específico para que el prestador solo pueda escribir una respuesta.
    """
    class Meta:
        model = Valoracion
        fields = ('respuesta_del_prestador',)
        extra_kwargs = {
            'respuesta_del_prestador': {'required': True}
        }
