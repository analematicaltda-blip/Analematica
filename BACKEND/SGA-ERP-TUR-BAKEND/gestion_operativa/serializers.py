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

class ScopedOperationalSerializer(serializers.ModelSerializer):
    def validate(self,attrs):
        provider=self.context.get('operational_provider')
        if provider is None:raise serializers.ValidationError('Contexto operativo autorizado requerido.')
        for name in ('provider','provider_id','inicio_real','fin_real','costo_real_acumulado'):
            if name in self.initial_data:raise serializers.ValidationError('Empresa, tiempos y costos reales no se asignan desde el formulario.')
        if 'estado' in self.initial_data:
            initial='PENDIENTE' if self.Meta.model.__name__=='OrdenOperativa' else 'PLANIFICADO'
            if self.instance is not None or self.Meta.model.__name__ not in {'OrdenOperativa','ProcesoOperativo'} or attrs.get('estado')!=initial:
                raise serializers.ValidationError('El estado se cambia mediante la ruta de transición auditada.')
        for name in ('orden','proceso'):
            parent=attrs.get(name) or getattr(self.instance,name,None)
            if parent is not None and (parent.provider_id!=provider.pk or not parent.is_active):
                raise serializers.ValidationError('La relación debe pertenecer a la empresa autorizada.')
        if self.instance and self.Meta.model.__name__ in {'OrdenOperativa','ProcesoOperativo'}:
            if self.instance.estado not in {'PENDIENTE','PREPARACION','PLANIFICADO'}:
                raise serializers.ValidationError('No se reescribe una operación activa o histórica desde CRUD.')
        begin=attrs.get('fecha_inicio',getattr(self.instance,'fecha_inicio',None))
        end=attrs.get('fecha_fin_estimada',getattr(self.instance,'fecha_fin_estimada',None))
        if begin and end and end<=begin:raise serializers.ValidationError('La fecha final debe ser posterior al inicio previsto.')
        if attrs.get('costo_proyectado',0)<0:raise serializers.ValidationError('Costo previsto no negativo requerido.')
        return attrs

class IncidenteOperativoSerializer(ScopedOperationalSerializer):
    class Meta:
        model = IncidenteOperativo
        read_only_fields = ('provider',)
        fields = '__all__'

class OrdenOperativaSerializer(ScopedOperationalSerializer):
    bitacora = RegistroOperativoSerializer(many=True, read_only=True)
    evidencias = EvidenciaOperativaSerializer(many=True, read_only=True)
    incidencias = serializers.SerializerMethodField()
    def get_incidencias(self,obj):
        return IncidenteOperativoSerializer(obj.incidencias.filter(provider_id=obj.provider_id,is_active=True),many=True,context=self.context).data

    class Meta:
        model = OrdenOperativa
        read_only_fields = ('provider','costo_real_acumulado')
        fields = '__all__'

class TareaOperativaSerializer(ScopedOperationalSerializer):
    class Meta:
        model = TareaOperativa
        read_only_fields = ('provider',)
        fields = '__all__'

class ProcesoOperativoSerializer(ScopedOperationalSerializer):
    tareas = serializers.SerializerMethodField()
    def get_tareas(self,obj):
        return TareaOperativaSerializer(obj.tareas.filter(provider_id=obj.provider_id,is_active=True),many=True,context=self.context).data
    class Meta:
        model = ProcesoOperativo
        read_only_fields = ('provider','inicio_real','fin_real')
        fields = '__all__'
