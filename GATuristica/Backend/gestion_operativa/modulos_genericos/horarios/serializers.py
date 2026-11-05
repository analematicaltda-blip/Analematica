from rest_framework import serializers
from .models import Horario, ExcepcionHorario

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ['id', 'dia_semana', 'hora_apertura', 'hora_cierre']

class ExcepcionHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcepcionHorario
        fields = ['id', 'fecha', 'esta_abierto', 'hora_apertura', 'hora_cierre', 'descripcion']

    def validate(self, data):
        if data.get('esta_abierto', False) and (data.get('hora_apertura') is None or data.get('hora_cierre') is None):
            raise serializers.ValidationError("Si el establecimiento está abierto, debe especificar hora de apertura y cierre.")
        if not data.get('esta_abierto', False):
            data['hora_apertura'] = None
            data['hora_cierre'] = None
        return data
