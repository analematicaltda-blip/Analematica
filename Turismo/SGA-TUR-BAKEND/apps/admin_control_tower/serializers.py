from rest_framework import serializers

class GlobalDashboardSerializer(serializers.Serializer):
    mrr = serializers.DecimalField(max_digits=15, decimal_places=2)
    arr = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_tenants = serializers.IntegerField()
    churn_rate = serializers.FloatField()

    # Financiero
    total_assets = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_liabilities = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=15, decimal_places=2)

class RiskPanelSerializer(serializers.Serializer):
    revenue_drop_detected = serializers.BooleanField()
    unbalanced_entries_count = serializers.IntegerField()
    tenants_in_arrears = serializers.IntegerField()
