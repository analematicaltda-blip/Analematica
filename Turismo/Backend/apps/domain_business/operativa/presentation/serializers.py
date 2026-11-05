from rest_framework import serializers
from apps.domain_business.operativa.models import ProviderProfile

class PerfilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ProviderProfile
        fields = [
            'id', 'user', 'commercial_name', 'provider_type',
            'is_verified'
        ]
        read_only_fields = ['user', 'is_verified']
