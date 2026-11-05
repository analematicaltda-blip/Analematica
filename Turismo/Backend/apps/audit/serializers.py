from rest_framework import serializers
from apps.audit.models import ForensicSecurityLog

class ForensicSecurityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForensicSecurityLog
        fields = '__all__'
