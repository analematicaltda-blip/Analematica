from rest_framework import serializers
from .domain.models import (
    TokenizedAsset,
    ProgrammableCapitalUnit,
    SmartGovernanceRule,
    DigitalRegistry,
    ComplianceConstraint
)

class TokenizedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenizedAsset
        fields = '__all__'

class ProgrammableUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammableCapitalUnit
        fields = '__all__'

class GovernanceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartGovernanceRule
        fields = '__all__'

class DigitalRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalRegistry
        fields = '__all__'

class ComplianceConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceConstraint
        fields = '__all__'
