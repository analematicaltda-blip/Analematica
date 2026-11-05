
from rest_framework import serializers
from apps.comercial.models import Plan, Subscription
from apps.domain_business.operativa.models import ProviderProfile

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'code', 'description', 'monthly_price',
            'yearly_price', 'target_user_type', 'is_active'
        ]

class SuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(), source='plan', write_only=True
    )
    # En el Super Admin, 'cliente' se mapea a 'perfil_ref_id' en el modelo unificado
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=ProviderProfile.objects.all(), source='perfil_ref_id', write_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_id', 'cliente_id', 'start_date', 'end_date',
            'is_active', 'status'
        ]
        read_only_fields = ('is_active', 'end_date')
