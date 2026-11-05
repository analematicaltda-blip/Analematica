from rest_framework import serializers
from .models import AlgorithmicCertificate, TrustSignal

class AlgorithmicCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmicCertificate
        fields = '__all__'

class TrustSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustSignal
        fields = '__all__'
