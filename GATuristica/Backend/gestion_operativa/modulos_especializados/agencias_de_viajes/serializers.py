# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/agencias_de_viajes/serializers.py
from rest_framework import serializers
from .models import PaqueteTuristico, ReservaPaquete

class PaqueteTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'nombre', 'descripcion', 'duracion_dias', 'precio_por_persona',
            'servicios_incluidos', 'estado', 'created_at', 'updated_at'
        ]
        read_only_fields = ('perfil',) # El perfil se asigna desde la vista

class ReservaPaqueteSerializer(serializers.ModelSerializer):
    # Opcional: mostrar detalles del paquete en la reserva
    paquete_nombre = serializers.CharField(source='paquete.nombre', read_only=True)

    class Meta:
        model = ReservaPaquete
        fields = [
            'id', 'paquete', 'paquete_nombre', 'nombre_cliente_temporal', 'email_cliente',
            'telefono_cliente', 'fecha_inicio', 'numero_de_personas',
            'costo_total', 'estado', 'notas_especiales', 'created_at'
        ]

    def validate_paquete(self, value):
        """
        Verifica que el paquete seleccionado pertenezca al prestador que está creando la reserva.
        """
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil_prestador'):
            if value.perfil != request.user.perfil_prestador:
                raise serializers.ValidationError("No tiene permiso para crear una reserva en este paquete.")
        return value

    def create(self, validated_data):
        # Calcula el costo total si no se proporciona
        if 'costo_total' not in validated_data:
            paquete = validated_data['paquete']
            numero_de_personas = validated_data.get('numero_de_personas', 1)
            validated_data['costo_total'] = paquete.precio_por_persona * numero_de_personas
        return super().create(validated_data)
