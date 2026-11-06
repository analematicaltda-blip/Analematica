from rest_framework import serializers
from .models import MetaEcosystem, EcosystemInterdependence, InteroperabilityProtocol, GlobalUtilityMetric, MetaLiquidityPool

class MetaEcosystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaEcosystem
        fields = '__all__'

class EcosystemInterdependenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcosystemInterdependence
        fields = '__all__'

class InteroperabilityProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteroperabilityProtocol
        fields = '__all__'

class GlobalUtilityMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalUtilityMetric
        fields = '__all__'

class MetaLiquidityPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaLiquidityPool
        fields = '__all__'

class MetaDashboardSerializer(serializers.Serializer):
    aggregate_global_utility = serializers.DecimalField(max_digits=25, decimal_places=4)
    network_health_index = serializers.DecimalField(max_digits=5, decimal_places=4)
    total_network_liquidity = serializers.DecimalField(max_digits=25, decimal_places=4)
    active_ecosystems = serializers.IntegerField()
    firewalls_active = serializers.IntegerField()
