from rest_framework import serializers
from .domain.kpi import KPI
from .domain.alert import Alert
from .domain.threshold import Threshold

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = '__all__'

class ExecutiveDashboardSerializer(serializers.Serializer):
    """
    Consolidated view for CEOs/CFOs.
    """
    total_revenue = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=18, decimal_places=2)
    ebitda = serializers.DecimalField(max_digits=18, decimal_places=2)
    burn_rate = serializers.DecimalField(max_digits=18, decimal_places=2)
    systemic_risk = serializers.FloatField()
    open_alerts_count = serializers.IntegerField()
    kpi_snapshots = KPISerializer(many=True)
    recent_alerts = AlertSerializer(many=True)
