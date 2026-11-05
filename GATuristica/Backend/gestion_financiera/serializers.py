from rest_framework import serializers
from .models import (
    CuentaBancaria, OrdenPago, TesoreriaCentral, EstadoResultados,
    BalanceGeneral, FlujoEfectivo, CambiosPatrimonio, ReservaFinanciera,
    ProyeccionFinanciera, RiesgoFinanciero, Presupuesto, LineaPresupuesto,
    CreditoFinanciero, CuotaCredito, IndicadorFinancieroHistorico,
    AlertaFinanciera, LogFinancieroInmutable
)

class TesoreriaCentralSerializer(serializers.ModelSerializer):
    class Meta:
        model = TesoreriaCentral
        fields = '__all__'

class EstadoResultadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoResultados
        fields = '__all__'

class BalanceGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceGeneral
        fields = '__all__'

class FlujoEfectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoEfectivo
        fields = '__all__'

class CambiosPatrimonioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambiosPatrimonio
        fields = '__all__'

class ReservaFinancieraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaFinanciera
        fields = '__all__'

class ProyeccionFinancieraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProyeccionFinanciera
        fields = '__all__'

class RiesgoFinancieroSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiesgoFinanciero
        fields = '__all__'

class CuentaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaBancaria
        fields = '__all__'

class OrdenPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenPago
        fields = '__all__'

class LineaPresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaPresupuesto
        fields = '__all__'

class PresupuestoSerializer(serializers.ModelSerializer):
    lineas = LineaPresupuestoSerializer(many=True, read_only=True)
    class Meta:
        model = Presupuesto
        fields = '__all__'

class CuotaCreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaCredito
        fields = '__all__'

class CreditoFinancieroSerializer(serializers.ModelSerializer):
    cuotas = CuotaCreditoSerializer(many=True, read_only=True)
    class Meta:
        model = CreditoFinanciero
        fields = '__all__'

class IndicadorFinancieroHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorFinancieroHistorico
        fields = '__all__'

class AlertaFinancieraSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaFinanciera
        fields = '__all__'

class LogFinancieroInmutableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogFinancieroInmutable
        fields = '__all__'
