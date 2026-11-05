from rest_framework import serializers
from .models import LegacyCustodian, LegacyMilestone, LegacyGuardrail

class LegacyCustodianSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = LegacyCustodian
        fields = ['id', 'username', 'appointed_at', 'is_active']

class LegacyMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyMilestone
        fields = '__all__'

class LegacyGuardrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyGuardrail
        fields = '__all__'
