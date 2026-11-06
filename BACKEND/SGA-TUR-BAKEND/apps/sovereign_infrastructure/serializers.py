from rest_framework import serializers
from .models import JurisdictionalNode, RegulatoryProfile, CapitalShield, DigitalInfraBackup, CorporateConstitution

class JurisdictionalNodeSerializer(serializers.ModelSerializer):
    resilience_index = serializers.SerializerMethodField()

    class Meta:
        model = JurisdictionalNode
        fields = '__all__'

    def get_resilience_index(self, obj):
        from .application.regulatory_service import RegulatoryIntelligenceService
        return RegulatoryIntelligenceService.calculate_sovereign_resilience(obj.id)

class RegulatoryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryProfile
        fields = '__all__'

class CapitalShieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalShield
        fields = '__all__'

class DigitalInfraBackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalInfraBackup
        fields = '__all__'

class CorporateConstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateConstitution
        fields = '__all__'

class SovereignDashboardSerializer(serializers.Serializer):
    resilience_score = serializers.DecimalField(max_digits=5, decimal_places=4)
    technical_independence = serializers.DecimalField(max_digits=5, decimal_places=4)
    capital_shield_total = serializers.DecimalField(max_digits=20, decimal_places=4)
    active_jurisdictions = serializers.IntegerField()
    active_backups = serializers.IntegerField()
