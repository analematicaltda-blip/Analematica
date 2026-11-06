from rest_framework import serializers
from .models import StrategyProposal, DecisionMatrix

class StrategyProposalSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    domain_display = serializers.CharField(source='get_domain_display', read_only=True)
    risk_display = serializers.CharField(source='get_nivel_riesgo_display', read_only=True)
    urgency_display = serializers.CharField(source='get_nivel_urgencia_display', read_only=True)
    decidida_por_name = serializers.CharField(source='decidida_por.username', read_only=True)

    class Meta:
        model = StrategyProposal
        fields = '__all__'

class DecisionMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionMatrix
        fields = '__all__'
