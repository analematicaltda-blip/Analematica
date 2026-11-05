from rest_framework import serializers
from .models import SaaSSubscription, CommercialKPI, SaaSInvoice, LeadPipelineLog
from .lead_model import SaaSLead
from .plan_model import SaaSPlan

class SaaSPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaaSPlan
        fields = '__all__'

class SaaSLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaaSLead
        fields = '__all__'

class LeadPipelineLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadPipelineLog
        fields = '__all__'

class SaaSSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = SaaSSubscription
        fields = '__all__'

class CommercialKPISerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialKPI
        fields = '__all__'

class SaaSInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaaSInvoice
        fields = '__all__'
