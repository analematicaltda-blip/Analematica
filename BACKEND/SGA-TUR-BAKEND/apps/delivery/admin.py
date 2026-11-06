from django.contrib import admin
from .models import DeliveryCompany, Driver, Vehicle, DeliveryService, DeliveryEvent, Ruta, IndicadorLogistico

@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'delivery_company', 'is_available')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'vehicle_type', 'delivery_company', 'is_active')

@admin.register(DeliveryService)
class DeliveryServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'tourist', 'status', 'estimated_price', 'created_at')
    list_filter = ('status', 'delivery_company')

@admin.register(DeliveryEvent)
class DeliveryEventAdmin(admin.ModelAdmin):
    list_display = ('service', 'event_type', 'timestamp')

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'zona', 'repartidor', 'activa')

@admin.register(IndicadorLogistico)
class IndicadorLogisticoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor', 'periodo', 'timestamp')
