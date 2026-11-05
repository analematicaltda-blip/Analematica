from rest_framework import serializers
from .models import DeliveryCompany, Driver, Vehicle, DeliveryService, DeliveryEvent, Ruta, IndicadorLogistico

class DeliveryCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCompany
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    class Meta:
        model = Driver
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'

class DeliveryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryEvent
        fields = '__all__'

class DeliveryServiceSerializer(serializers.ModelSerializer):
    events = DeliveryEventSerializer(many=True, read_only=True)
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    class Meta:
        model = DeliveryService
        fields = '__all__'

class IndicadorLogisticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorLogistico
        fields = '__all__'
