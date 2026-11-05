from rest_framework import serializers
from .models import GlobalLedgerEntry, SchemaRegistry, RegulatorySyncNode, DigitalIdentity, DataFabricRegion

class GlobalLedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalLedgerEntry
        fields = '__all__'

class SchemaRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaRegistry
        fields = '__all__'

class RegulatorySyncNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatorySyncNode
        fields = '__all__'

class DigitalIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalIdentity
        fields = '__all__'

class DataFabricRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFabricRegion
        fields = '__all__'

class GDEIDashboardSerializer(serializers.Serializer):
    interoperability_index = serializers.DecimalField(max_digits=10, decimal_places=4)
    total_ledger_entries = serializers.IntegerField()
    active_schemas = serializers.IntegerField()
    verified_identities = serializers.IntegerField()
    global_health_status = serializers.CharField()
