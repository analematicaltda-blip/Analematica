from rest_framework import serializers
from ..models.provider_models import TourismProvider,BusinessProfile,TourismService,Reservation


def administrator(user):
    return bool(user and user.is_authenticated and user.is_active and user.is_superuser)

class OwnedProviderSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields=super().get_fields()
        if 'provider' in fields:
            request=self.context.get('request');user=getattr(request,'user',None)
            fields['provider'].queryset=TourismProvider.objects.all() if administrator(user) else TourismProvider.objects.filter(owner=user) if user and user.is_authenticated else TourismProvider.objects.none()
        return fields

    def validate_provider(self,value):
        if self.instance and value.pk!=self.instance.provider_id:
            raise serializers.ValidationError('No se puede trasladar este registro a otro prestador.')
        return value

class BusinessProfileSerializer(OwnedProviderSerializer):
    class Meta:
        model=BusinessProfile
        fields='__all__'
        read_only_fields=['id','created_at','updated_at']

class TourismProviderSerializer(serializers.ModelSerializer):
    business_profile=BusinessProfileSerializer(read_only=True)
    class Meta:
        model=TourismProvider
        fields='__all__'
        read_only_fields=['id','owner','created_at','updated_at','rnt_validated','rnt_last_sync','puntuacion_capacitacion','puntuacion_verificacion','puntuacion_resenas','puntuacion_total']

class TourismServiceSerializer(OwnedProviderSerializer):
    class Meta:
        model=TourismService
        fields='__all__'
        read_only_fields=['id','created_at','updated_at']

    def validate_price(self,value):
        if value<0:raise serializers.ValidationError('El precio no puede ser negativo.')
        return value

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reservation
        # Internal metadata is not customer/provider API output.
        fields=['id','provider','service','customer','start_date','end_date','status','total_price','created_at','updated_at','is_active']
        read_only_fields=fields
