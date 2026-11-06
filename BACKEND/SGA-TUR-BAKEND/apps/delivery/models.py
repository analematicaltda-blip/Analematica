import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DeliveryCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    company_id = models.UUIDField(unique=True, null=True, blank=True, help_text="ID de la Company (aislamiento DB)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def company(self):
        from apps.companies.models import Company
        return Company.objects.filter(id=self.company_id).first()

    def __str__(self):
        return self.name

class Driver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(unique=True, null=True, blank=True, help_text="ID del CustomUser (aislamiento DB)")
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE, related_name='drivers')
    license_number = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.delivery_company.name}"

class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        MOTO = "MOTO", _("Motocicleta")
        MOTOCARRO = "MOTOCARRO", _("Motocarro")
        AUTO = "AUTO", _("Automóvil")
        VAN = "VAN", _("Camioneta / Van")
        BICICLETA = "BICICLETA", _("Bicicleta")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plate = models.CharField(max_length=20, unique=True, null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE, related_name='vehicles')
    current_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_vehicles')
    is_active = models.BooleanField(default=True)

    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=5.0)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate or 'N/A'} ({self.vehicle_type})"

class Ruta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    zona = models.CharField(max_length=100)
    repartidor = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas')
    activa = models.BooleanField(default=True)

    geodata = models.JSONField(default=dict, help_text="Coordenadas de la ruta optimizada")
    tiempo_estimado_mins = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ruta {self.nombre} - {self.zona}"

class DeliveryService(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "PENDIENTE", _("Pendiente")
        EN_PREPARACION = "EN_PREPARACION", _("En Preparación")
        LISTO_DESPACHO = "LISTO_DESPACHO", _("Listo para Despacho")
        EN_RUTA = "EN_RUTA", _("En Ruta")
        ENTREGADO = "ENTREGADO", _("Entregado")
        FALLIDO = "FALLIDO", _("Fallido")
        REPROGRAMADO = "REPROGRAMADO", _("Reprogramado")
        CANCELADO = "CANCELADO", _("Cancelado")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tourist_id = models.IntegerField(null=True, blank=True, help_text="ID del CustomUser (aislamiento DB)")

    # Tenant alignment
    provider_id = models.UUIDField(null=True, blank=True, help_text="ID del ProviderProfile")

    # --- Territorial & Classification ---
    department_code = models.CharField(max_length=2, blank=True, null=True)
    municipality_code = models.CharField(max_length=5, blank=True, null=True)
    sub_classification = models.CharField(max_length=150, blank=True, null=True)

    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')

    origin_address = models.CharField(max_length=500)
    destination_address = models.CharField(max_length=500)

    prioridad = models.CharField(max_length=20, default='NORMAL') # ALTA, MEDIA, NORMAL

    estimated_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    comision_repartidor = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    value_declared = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDIENTE)

    wallet_transaction = models.UUIDField(null=True, blank=True, help_text="ID de la transacción en apps.wallet")
    governance_intention_id = models.CharField(max_length=255, null=True, blank=True)

    # Interoperabilidad
    related_operational_order_id = models.UUIDField(null=True, blank=True)

    # Feedback
    rating = models.PositiveIntegerField(null=True, blank=True)
    tourist_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def driver_user(self):
        from api.models import CustomUser
        return CustomUser.objects.filter(id=self.user_id).first()

    @property
    def tourist(self):
        from api.models import CustomUser
        return CustomUser.objects.filter(id=self.tourist_id).first()

    def __str__(self):
        return f"Delivery {self.id} - {self.status}"

class DeliveryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(DeliveryService, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class EvidenciaEntrega(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.OneToOneField(DeliveryService, on_delete=models.CASCADE, related_name='evidencia')
    foto = models.ImageField(upload_to='delivery/evidencias/', null=True, blank=True)
    firma_digital = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class DeliveryEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(DeliveryService, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class DeliveryIncident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(DeliveryService, on_delete=models.CASCADE, related_name='incidents')
    severity = models.CharField(max_length=20, default='MEDIUM') # LOW, MEDIUM, HIGH, CRITICAL
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class DeliveryLiquidation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.OneToOneField(DeliveryService, on_delete=models.CASCADE, related_name='liquidation')
    total_to_provider = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_to_driver = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_processed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class DeliveryPenalty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='penalties')
    delivery = models.ForeignKey(DeliveryService, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    reason = models.CharField(max_length=255)
    applied = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class IndicadorLogistico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_id = models.UUIDField() # Tenant
    nombre = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    periodo = models.CharField(max_length=20) # YYYY-MM
    timestamp = models.DateTimeField(auto_now_add=True)
