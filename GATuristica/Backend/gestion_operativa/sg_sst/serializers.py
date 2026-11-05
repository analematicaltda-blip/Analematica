from rest_framework import serializers
from .models import (
    MatrizRiesgo, ControlRiesgo, IncidenteLaboral, InvestigacionIncidente,
    SaludOcupacional, CapacitacionSST, PlanAnualSST, ActividadPlanSST,
    InspeccionSST, HallazgoInspeccion, IndicadorSST, AlertaSST
)

class ControlRiesgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlRiesgo
        fields = '__all__'

class MatrizRiesgoSerializer(serializers.ModelSerializer):
    controles = ControlRiesgoSerializer(many=True, read_only=True)
    class Meta:
        model = MatrizRiesgo
        fields = '__all__'

class InvestigacionIncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestigacionIncidente
        fields = '__all__'

class IncidenteLaboralSerializer(serializers.ModelSerializer):
    investigacion = InvestigacionIncidenteSerializer(read_only=True)
    class Meta:
        model = IncidenteLaboral
        fields = '__all__'

class ActividadPlanSSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadPlanSST
        fields = '__all__'

class PlanAnualSSTSerializer(serializers.ModelSerializer):
    actividades = ActividadPlanSSTSerializer(many=True, read_only=True)
    class Meta:
        model = PlanAnualSST
        fields = '__all__'

class HallazgoInspeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HallazgoInspeccion
        fields = '__all__'

class InspeccionSSTSerializer(serializers.ModelSerializer):
    hallazgos = HallazgoInspeccionSerializer(many=True, read_only=True)
    class Meta:
        model = InspeccionSST
        fields = '__all__'

class IndicadorSSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorSST
        fields = '__all__'

class AlertaSSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaSST
        fields = '__all__'

class SaludOcupacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaludOcupacional
        fields = '__all__'

class CapacitacionSSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacitacionSST
        fields = '__all__'
