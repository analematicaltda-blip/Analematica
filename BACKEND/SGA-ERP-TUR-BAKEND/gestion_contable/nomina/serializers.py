from rest_framework import serializers
from .models import (
    Empleado, Contrato, Planilla, NovedadNomina, ConceptoNomina,
    DetalleLiquidacion, IncapacidadLaboral, Ausencia, ProvisionNomina,
    IndicadorLaboral, HistorialSalarial
)
from decimal import Decimal

class HistorialSalarialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialSalarial
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    historial_salarial = HistorialSalarialSerializer(many=True, read_only=True)
    class Meta:
        model = Contrato
        fields = '__all__'

class EmpleadoSerializer(serializers.ModelSerializer):
    contratos = ContratoSerializer(many=True, read_only=True)

    class Meta:
        model = Empleado
        fields = '__all__'
        read_only_fields = ('perfil',)

class ConceptoNominaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoNomina
        fields = '__all__'

class NovedadNominaSerializer(serializers.ModelSerializer):
    concepto_detalle = ConceptoNominaSerializer(source='concepto', read_only=True)
    class Meta:
        model = NovedadNomina
        fields = '__all__'

class DetalleLiquidacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre', read_only=True)
    empleado_apellido = serializers.CharField(source='empleado.apellido', read_only=True)
    class Meta:
        model = DetalleLiquidacion
        fields = '__all__'

class PlanillaSerializer(serializers.ModelSerializer):
    detalles_liquidacion = DetalleLiquidacionSerializer(many=True, read_only=True)
    class Meta:
        model = Planilla
        fields = '__all__'
        read_only_fields = ('perfil', 'total_devengado', 'total_deduccion', 'total_neto')

class IncapacidadLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncapacidadLaboral
        fields = '__all__'

class AusenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ausencia
        fields = '__all__'

class ProvisionNominaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionNomina
        fields = '__all__'

class IndicadorLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorLaboral
        fields = '__all__'
