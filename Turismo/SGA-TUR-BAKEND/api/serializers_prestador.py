from rest_framework import serializers
from .models import ServicioTuristico, Booking, Factura

class ServicioTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioTuristico
        fields = '__all__'
        read_only_fields = ('prestador',)

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'
        read_only_fields = ('prestador', 'cliente')