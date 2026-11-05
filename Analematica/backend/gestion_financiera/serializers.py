from rest_framework import serializers
from apps.admin_plataforma.gestion_financiera.models import CuentaBancaria, OrdenPago

class AdminCuentaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaBancaria
        fields = '__all__'
        read_only_fields = ['perfil_ref_id']

class AdminOrdenPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenPago
        fields = '__all__'
