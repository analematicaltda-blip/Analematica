from rest_framework import serializers
from ..models.provider_models import TourismProvider, BusinessProfile, TourismService, Reservation

class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = '__all__'

class TourismProviderSerializer(serializers.ModelSerializer):
    business_profile = BusinessProfileSerializer(read_only=True)

    class Meta:
        model = TourismProvider
        fields = '__all__'
        read_only_fields = ['owner']

class TourismServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismService
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
