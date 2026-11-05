from rest_framework import serializers
from .models import Operator, OperatorTracking, OperationReport

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'

class OperatorTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorTracking
        fields = '__all__'

class OperationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationReport
        fields = '__all__'
