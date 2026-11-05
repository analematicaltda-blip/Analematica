from rest_framework import serializers

class FinancialSummarySerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    total_adq_costs = serializers.FloatField()
    avg_cac = serializers.FloatField()

class ROIAnalysisSerializer(serializers.Serializer):
    dimension = serializers.CharField()
    roi = serializers.FloatField()
    cac = serializers.FloatField()
    ltv = serializers.FloatField()

class FinancialDashboardSerializer(serializers.Serializer):
    summary = FinancialSummarySerializer()
    recent_events = serializers.ListField(child=serializers.DictField())
