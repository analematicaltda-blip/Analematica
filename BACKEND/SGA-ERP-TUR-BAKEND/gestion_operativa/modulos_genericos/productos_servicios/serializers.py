from rest_framework import serializers
from uuid import UUID
from .models import Product
from ....company_scope import owned_provider

class MoneyAmountField(serializers.DecimalField):
    def to_representation(self,value):
        return super().to_representation(getattr(value,'amount',value))

class ProductSerializer(serializers.ModelSerializer):
    base_price=MoneyAmountField(max_digits=19,decimal_places=2)

    class Meta:
        model=Product
        fields='__all__'
        read_only_fields=['provider','id_publico','id','created_at','updated_at']

    def get_fields(self):
        fields=super().get_fields()
        request=self.context.get('request')
        if request is not None and 'cancellation_policy' in fields:
            fields['cancellation_policy'].queryset=fields['cancellation_policy'].queryset.filter(perfil_ref_id=owned_provider(request).pk)
        return fields

    def validate(self,attrs):
        request=self.context.get('request')
        if request is not None:
            provider=owned_provider(request)
            if 'provider' in self.initial_data:
                try:submitted=UUID(str(self.initial_data['provider']))
                except (TypeError,ValueError):raise serializers.ValidationError({'provider':'Prestador inválido.'})
                if submitted!=provider.pk:raise serializers.ValidationError({'provider':'No se puede trasladar el producto a otra empresa.'})
            policy=attrs.get('cancellation_policy')
            if policy is not None and policy.perfil_ref_id!=provider.pk:raise serializers.ValidationError({'cancellation_policy':'Política ajena a la empresa.'})
        price=attrs.get('base_price')
        if price is not None and getattr(price,'amount',price)<0:raise serializers.ValidationError({'base_price':'El precio no puede ser negativo.'})
        return attrs
