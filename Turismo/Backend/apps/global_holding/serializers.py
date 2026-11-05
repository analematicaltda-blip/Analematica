from rest_framework import serializers
from .domain.models import (
    JurisdictionConfig,
    GlobalCapitalAllocator,
    TaxStrategy,
    TreasuryPosition,
    MacroScenario
)

class JurisdictionConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = JurisdictionConfig
        fields = '__all__'

class GlobalCapitalAllocatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCapitalAllocator
        fields = '__all__'

class TaxStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxStrategy
        fields = '__all__'

class TreasuryPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreasuryPosition
        fields = '__all__'

class MacroScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroScenario
        fields = '__all__'
