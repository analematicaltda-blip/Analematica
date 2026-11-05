from rest_framework import serializers
from .models import Reserva, PoliticaCancelacion, ReservaServicioAdicional
from ..productos_servicios.serializers import ProductSerializer
from ..clientes.serializers import ClienteSerializer

class PoliticaCancelacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaCancelacion
        fields = '__all__'
        read_only_fields = ('perfil',)

class ReservaServicioAdicionalSerializer(serializers.ModelSerializer):
    servicio_id = serializers.UUIDField(source='servicio_ref_id')

    class Meta:
        model = ReservaServicioAdicional
        fields = ('servicio_id', 'cantidad', 'precio_unitario')

class ReservaSerializer(serializers.ModelSerializer):
    servicios_adicionales = ReservaServicioAdicionalSerializer(many=True, required=False)
    # producto_info = ProductSerializer(source='producto', read_only=True)
    cliente_id = serializers.UUIDField(source='cliente_ref_id')
    # cliente_info = ClienteSerializer(source='cliente', read_only=True)

    # Interoperabilidad (FASE 9)
    related_deliveries = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id', 'id_publico', 'cliente_id', 'estado',
            'fecha_inicio', 'fecha_fin',
            'precio_total', 'deposito_pagado',
            'notas',
            'servicios_adicionales',
            'related_deliveries'
        ]
        read_only_fields = ('perfil',)

    def create(self, validated_data):
        servicios_data = validated_data.pop('servicios_adicionales', [])

        # Endurecimiento N6: Cálculo Determinístico de Costos
        precio_total = Decimal('0.00')
        # Si el producto está vinculado, obtener precio base
        # (Aquí se asume que precio_total ya viene calculado del frontend o se valida)
        # Para el endurecimiento, aseguramos que la suma de servicios adicionales sea correcta.

        servicios_suma = sum(Decimal(str(s.get('precio_unitario', 0))) * s.get('cantidad', 1) for s in servicios_data)

        # Nota: Reserva original ya trae un precio_total (base)
        base = Decimal(str(validated_data.get('precio_total', 0)))
        validated_data['precio_total'] = base + servicios_suma

        reserva = Reserva.objects.create(**validated_data)
        for servicio_data in servicios_data:
            ReservaServicioAdicional.objects.create(reserva=reserva, **servicio_data)

        # Emisión de Evento para Contabilidad (Fase 3 Bridge)
        from apps.core_erp.event_bus import EventBus
        EventBus.emit("RESERVATION_CREATED", {
            "tenant_id": str(reserva.perfil_id),
            "total_amount": float(reserva.precio_total),
            "reference": str(reserva.id_publico)
        })

        return reserva

    def get_related_deliveries(self, obj):
        from apps.delivery.models import DeliveryService
        from apps.delivery.serializers import DeliveryServiceSerializer
        deliveries = DeliveryService.objects.filter(related_operational_order_id=obj.id)
        return DeliveryServiceSerializer(deliveries, many=True).data

    def update(self, instance, validated_data):
        servicios_data = validated_data.pop('servicios_adicionales', None)
        # TODO: Recalcular costo si cambian los datos base
        instance = super().update(instance, validated_data)

        if servicios_data is not None:
            instance.servicios_adicionales.all().delete()
            for servicio_data in servicios_data:
                ReservaServicioAdicional.objects.create(reserva=instance, **servicio_data)

        return instance
