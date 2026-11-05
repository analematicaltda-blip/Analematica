# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/arrendadoras_vehiculos/serializers.py
from rest_framework import serializers
from .models import VehiculoDeAlquiler, Alquiler
from django.utils import timezone

class VehiculoDeAlquilerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculoDeAlquiler
        fields = [
            'id', 'nombre', 'placa', 'categoria', 'transmision',
            'numero_pasajeros', 'precio_por_dia', 'disponible'
        ]
        read_only_fields = ('perfil', 'disponible',)

class AlquilerSerializer(serializers.ModelSerializer):
    # Opcional: mostrar detalles del vehículo en la reserva
    vehiculo_nombre = serializers.CharField(source='vehiculo.nombre', read_only=True)
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)

    class Meta:
        model = Alquiler
        fields = [
            'id', 'vehiculo', 'vehiculo_nombre', 'vehiculo_placa', 'nombre_cliente_temporal',
            'email_cliente', 'fecha_recogida', 'fecha_devolucion',
            'costo_total_calculado', 'estado'
        ]
        read_only_fields = ('costo_total_calculado',)

    def validate_vehiculo(self, value):
        """
        Verifica que el vehículo seleccionado pertenezca al prestador.
        """
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil_prestador'):
            if value.perfil != request.user.perfil_prestador:
                raise serializers.ValidationError("No tiene permiso para gestionar este vehículo.")
        return value

    def validate(self, data):
        """
        Valida que la fecha de devolución sea posterior a la fecha de recogida.
        """
        if data['fecha_recogida'] >= data['fecha_devolucion']:
            raise serializers.ValidationError("La fecha de devolución debe ser posterior a la fecha de recogida.")

        if data['fecha_recogida'] < timezone.now():
            # Permite editar alquileres pasados, pero no crear nuevos en el pasado
            if not self.instance:
                 raise serializers.ValidationError("La fecha de recogida no puede ser en el pasado.")

        return data
