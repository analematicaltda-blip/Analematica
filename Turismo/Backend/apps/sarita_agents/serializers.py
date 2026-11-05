# backend/apps/sarita_agents/serializers.py
from rest_framework import serializers
from .models import Mision, PlanTáctico, TareaDelegada, RegistroDeEjecucion, MicroTarea, RegistroMicroTarea

class RegistroMicroTareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroMicroTarea
        fields = '__all__'

class MicroTareaSerializer(serializers.ModelSerializer):
    logs = RegistroMicroTareaSerializer(many=True, read_only=True)
    class Meta:
        model = MicroTarea
        fields = '__all__'

class RegistroDeEjecucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroDeEjecucion
        fields = '__all__'

class TareaDelegadaSerializer(serializers.ModelSerializer):
    logs_ejecucion = RegistroDeEjecucionSerializer(many=True, read_only=True)
    micro_tareas = MicroTareaSerializer(many=True, read_only=True)
    class Meta:
        model = TareaDelegada
        fields = '__all__'

class PlanTácticoSerializer(serializers.ModelSerializer):
    tareas = TareaDelegadaSerializer(many=True, read_only=True)
    class Meta:
        model = PlanTáctico
        fields = '__all__'

class MisionSerializer(serializers.ModelSerializer):
    planes_tacticos = PlanTácticoSerializer(many=True, read_only=True)
    class Meta:
        model = Mision
        fields = '__all__'

class DirectiveSerializer(serializers.Serializer):
    """
    Serializador para validar la estructura de la directiva de entrada.
    No se vincula a un modelo.
    """
    domain = serializers.CharField(required=True)
    mission = serializers.JSONField(required=True)
    idempotency_key = serializers.UUIDField(required=False)
