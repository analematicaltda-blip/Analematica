from rest_framework import serializers
from .models import Funnel, FunnelVersion

class FunnelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunnelVersion
        fields = ['id', 'version_number', 'schema_json', 'created_at', 'is_active']

class FunnelSerializer(serializers.ModelSerializer):
    # Mostramos la última versión para simplificar la respuesta del listado
    latest_version = FunnelVersionSerializer(source='versions.first', read_only=True)

    class Meta:
        model = Funnel
        fields = ['id', 'name', 'status', 'created_at', 'updated_at', 'latest_version']
        read_only_fields = ['status', 'created_at', 'updated_at']
