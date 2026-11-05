
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'status', 'provider', 'transaction_id', 'created_at']

class InitiatePaymentSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=50)
