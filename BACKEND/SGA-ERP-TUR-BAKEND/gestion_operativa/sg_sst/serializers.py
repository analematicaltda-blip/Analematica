from rest_framework import serializers
from .models import (
    MatrizRiesgo, ControlRiesgo, IncidenteLaboral, InvestigacionIncidente,
    SaludOcupacional, CapacitacionSST, PlanAnualSST, ActividadPlanSST,
    InspeccionSST, HallazgoInspeccion, IndicadorSST, AlertaSST
)

class ScopedSSTSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for name in ('provider', 'created_at', 'updated_at', 'porcentaje_cumplimiento', 'porcentaje_hallazgos_cerrados'):
            if name in fields:
                fields[name].read_only = True
        provider = self.context.get('sst_provider')
        if 'plan' in fields:
            fields['plan'].queryset = PlanAnualSST.objects.filter(provider_id=provider.pk) if provider else PlanAnualSST.objects.none()
        return fields

    def validate(self, attrs):
        provider = self.context.get('sst_provider')
        if provider is None:
            raise serializers.ValidationError('Contexto empresarial verificado requerido.')
        supplied = self.initial_data.get('provider') if hasattr(self, 'initial_data') else None
        if supplied is not None:
            from uuid import UUID
            try:
                matches = UUID(str(supplied)) == provider.pk
            except (ValueError, TypeError, AttributeError):
                matches = False
            if not matches:
                raise serializers.ValidationError('La empresa del contenido contradice el contexto autorizado.')
        if self.instance is not None and hasattr(self.instance, 'provider_id') and self.instance.provider_id != provider.pk:
            raise serializers.ValidationError('Registro ajeno a la empresa.')
        return attrs

class ControlRiesgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlRiesgo
        fields = '__all__'

class MatrizRiesgoSerializer(ScopedSSTSerializer):
    probabilidad = serializers.IntegerField(min_value=1, max_value=4)
    consecuencia = serializers.IntegerField(min_value=1, max_value=4)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        process = attrs.get('proceso_operativo_ref_id')
        if process:
            from ..models import ProcesoOperativo
            if not ProcesoOperativo.objects.filter(pk=process, provider=self.context['sst_provider']).exists():
                raise serializers.ValidationError('Proceso ajeno o inexistente.')
        return attrs

    controles = ControlRiesgoSerializer(many=True, read_only=True)
    class Meta:
        model = MatrizRiesgo
        fields = '__all__'

class InvestigacionIncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestigacionIncidente
        fields = '__all__'

class IncidenteLaboralSerializer(ScopedSSTSerializer):
    investigacion = InvestigacionIncidenteSerializer(read_only=True)
    class Meta:
        model = IncidenteLaboral
        fields = '__all__'

class ActividadPlanSSTSerializer(ScopedSSTSerializer):
    class Meta:
        model = ActividadPlanSST
        fields = '__all__'

class PlanAnualSSTSerializer(ScopedSSTSerializer):
    actividades = ActividadPlanSSTSerializer(many=True, read_only=True)
    class Meta:
        model = PlanAnualSST
        fields = '__all__'

class HallazgoInspeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HallazgoInspeccion
        fields = '__all__'

class InspeccionSSTSerializer(ScopedSSTSerializer):
    hallazgos = HallazgoInspeccionSerializer(many=True, read_only=True)
    class Meta:
        model = InspeccionSST
        fields = '__all__'

class IndicadorSSTSerializer(ScopedSSTSerializer):
    class Meta:
        model = IndicadorSST
        fields = '__all__'

class AlertaSSTSerializer(ScopedSSTSerializer):
    class Meta:
        model = AlertaSST
        fields = '__all__'

class SaludOcupacionalSerializer(ScopedSSTSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        from ...gestion_contable.nomina.models import Empleado
        employee = attrs.get('empleado_id', self.instance.empleado_id if self.instance else None)
        if not Empleado.objects.filter(pk=employee, perfil_id=self.context['sst_provider'].pk).exists():
            raise serializers.ValidationError('Empleado ajeno o inexistente.')
        return attrs

    class Meta:
        model = SaludOcupacional
        fields = '__all__'

class CapacitacionSSTSerializer(ScopedSSTSerializer):
    class Meta:
        model = CapacitacionSST
        fields = '__all__'
