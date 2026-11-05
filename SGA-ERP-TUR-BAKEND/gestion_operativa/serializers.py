from rest_framework import serializers
from .models import ProcesoOperativo, TareaOperativa, OrdenOperativa, RegistroOperativo, EvidenciaOperativa, IncidenteOperativo

class RegistroOperativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroOperativo
        fields = '__all__'

class EvidenciaOperativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenciaOperativa
        fields = '__all__'

class IncidenteOperativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidenteOperativo
        fields = '__all__'

class OrdenOperativaSerializer(serializers.ModelSerializer):
    bitacora = RegistroOperativoSerializer(many=True, read_only=True)
    evidencias = EvidenciaOperativaSerializer(many=True, read_only=True)
    incidencias = IncidenteOperativoSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenOperativa
        fields = '__all__'

class TareaOperativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaOperativa
        fields = '__all__'

class ProcesoOperativoSerializer(serializers.ModelSerializer):
    tareas = TareaOperativaSerializer(many=True, read_only=True)
    class Meta:
        model = ProcesoOperativo
        fields = '__all__'
