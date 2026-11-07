from rest_framework import serializers
from .models import Presupuesto, PartidaPresupuestal, EjecucionPresupuestal

class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = ['id', 'nombre', 'ano_fiscal', 'total_ingresos_presupuestado', 'total_gastos_presupuestado']

class PartidaPresupuestalSerializer(serializers.ModelSerializer):
    cuenta_contable_nombre = serializers.CharField(source='cuenta_contable.name', read_only=True)

    class Meta:
        model = PartidaPresupuestal
        fields = ['id', 'presupuesto', 'cuenta_contable', 'cuenta_contable_nombre', 'tipo', 'monto_presupuestado', 'monto_ejecutado']
        read_only_fields = ('monto_ejecutado',)

class EjecucionPresupuestalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EjecucionPresupuestal
        fields = ['id', 'partida', 'fecha', 'monto', 'descripcion']
