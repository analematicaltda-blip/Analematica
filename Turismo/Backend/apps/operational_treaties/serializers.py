from rest_framework import serializers
from .models import OperationalTreaty, TreatyComplianceAudit, SovereignKillSwitch

class OperationalTreatySerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalTreaty
        fields = '__all__'

class TreatyComplianceAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatyComplianceAudit
        fields = '__all__'
