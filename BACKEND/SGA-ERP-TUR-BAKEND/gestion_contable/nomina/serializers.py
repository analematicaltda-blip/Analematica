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
    posting_verification = serializers.SerializerMethodField()

    def get_posting_verification(self, obj):
        return 'NOT_POSTED' if obj.estado == 'BORRADOR' else 'NOT_VERIFIED'

    detalles_liquidacion = DetalleLiquidacionSerializer(many=True, read_only=True)
    def validate(self, attrs):
        provider = self.context.get('payroll_provider')
        if provider is None:
            raise serializers.ValidationError('Contexto empresarial verificado requerido.')
        initial = self.initial_data
        for name in ('estado', 'asiento_contable_ref_id', 'orden_pago_ref_id', 'evidencia_archivistica_ref_id'):
            if name in initial:
                raise serializers.ValidationError('El estado y las referencias financieras se asignan únicamente por un flujo verificado.')
        if 'perfil' in initial and str(initial['perfil']) != str(provider.pk):
            raise serializers.ValidationError('Empresa contradictoria.')
        start = attrs.get('periodo_inicio', self.instance.periodo_inicio if self.instance else None)
        end = attrs.get('periodo_fin', self.instance.periodo_fin if self.instance else None)
        if start is not None and end is not None and start > end:
            raise serializers.ValidationError('Período inválido.')
        return attrs

    class Meta:
        model = Planilla
        fields = '__all__'
        read_only_fields = ('perfil', 'total_devengado', 'total_deduccion', 'total_neto', 'estado', 'asiento_contable_ref_id', 'orden_pago_ref_id', 'evidencia_archivistica_ref_id')

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
