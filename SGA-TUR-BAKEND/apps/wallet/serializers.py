from rest_framework import serializers
from .models import Wallet, WalletTransaccion, WalletMovimiento

class WalletAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('saldo_disponible', 'saldo_bloqueado', 'saldo_en_proceso', 'estado')

class WalletMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMovimiento
        fields = '__all__'

class WalletTransactionSerializer(serializers.ModelSerializer):
    movimientos = WalletMovimientoSerializer(many=True, read_only=True)

    class Meta:
        model = WalletTransaccion
        fields = '__all__'
