from rest_framework import serializers
from .models import Plan, Subscription, AddOn, UsageMetric

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = PlanSerializer(source='plan', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'tenant_id', 'plan', 'plan_details', 'status',
            'billing_cycle', 'start_date', 'next_billing_date',
            'is_active', 'cancel_at_period_end'
        ]

class UsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageMetric
        fields = '__all__'
