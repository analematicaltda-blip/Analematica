from rest_framework import serializers
from decimal import Decimal
from .models import Wallet,WalletTransaccion,WalletMovimiento,WalletTransferIntent,WalletDeviceCredential

class WalletAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=Wallet
        fields=['id','owner_type','currency','saldo_disponible','saldo_bloqueado','saldo_en_proceso','estado','updated_at']
        read_only_fields=fields

class WalletMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model=WalletMovimiento
        fields=['id','wallet','tipo','monto','timestamp']
        read_only_fields=fields

class WalletTransactionSerializer(serializers.ModelSerializer):
    movimientos=serializers.SerializerMethodField()
    currency=serializers.SerializerMethodField()
    def get_movimientos(self,instance):
        user=self.context['request'].user
        rows=instance.movimientos.all()
        from .services.access_policy import accessible_wallets
        rows=rows.filter(wallet__in=accessible_wallets(user))
        return WalletMovimientoSerializer(rows,many=True).data
    def get_currency(self,instance):return instance.metadata.get('currency','')
    class Meta:
        model=WalletTransaccion
        fields=['id','monto_total','estado','timestamp','currency','movimientos']
        read_only_fields=fields

class TransferIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model=WalletTransferIntent
        fields=['id','source','destination','amount','currency','digest','state','expires_at','reviewed_at','executed_at','transaction']
        read_only_fields=fields

class PrepareTransferSerializer(serializers.Serializer):
    source=serializers.UUIDField()
    destination=serializers.UUIDField()
    amount=serializers.DecimalField(max_digits=18,decimal_places=2,min_value=Decimal('0.01'))
    idempotency_key=serializers.UUIDField()

class DeviceProofSerializer(serializers.Serializer):
    challenge=serializers.UUIDField()
    signature=serializers.CharField(min_length=8,max_length=128,trim_whitespace=False,write_only=True)

class ReviewTransferSerializer(serializers.Serializer):
    digest=serializers.RegexField(r'^[a-f0-9]{64}$')
    device_proof=DeviceProofSerializer(required=False,write_only=True)

class ExecuteTransferSerializer(ReviewTransferSerializer):
    confirmation=serializers.CharField(min_length=32,max_length=128,trim_whitespace=False,write_only=True)

class DeviceChallengeSerializer(serializers.Serializer):
    credential=serializers.UUIDField()
    phase=serializers.ChoiceField(choices=['REVIEW','EXECUTE'])

class DeviceAttestationSerializer(serializers.Serializer):
    enrollment_authorization=serializers.CharField(max_length=4096,trim_whitespace=False,write_only=True)
    public_key=serializers.CharField(max_length=128,trim_whitespace=False)
    certificate_chain=serializers.ListField(child=serializers.CharField(max_length=24000,trim_whitespace=False),min_length=1,max_length=8)

class DeviceCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model=WalletDeviceCredential
        fields=['id','audience','status','verified_at','valid_until','revoked_at','created_at']
        read_only_fields=fields
