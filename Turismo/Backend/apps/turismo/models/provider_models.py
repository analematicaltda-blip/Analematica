from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class TourismProvider(BaseModel):
    class ProviderType(models.TextChoices):
        HOTEL = 'HOTEL', _('Hotel')
        RESTAURANT = 'RESTAURANT', _('Restaurante')
        GUIDE = 'GUIDE', _('Guía Turístico')
        TRAVEL_AGENCY = 'TRAVEL_AGENCY', _('Agencia de Viajes')
        TOUR_OPERATOR = 'TOUR_OPERATOR', _('Operador Turístico')
        TRANSPORT = 'TRANSPORT', _('Transporte Turístico')
        VEHICLE_RENTAL = 'VEHICLE_RENTAL', _('Alquiler de Vehículos')
        ARTISAN = 'ARTISAN', _('Artesano')
        EVENT_ORGANIZER = 'EVENT_ORGANIZER', _('Organizador de Eventos')
        EXPERIENCE_PROVIDER = 'EXPERIENCE_PROVIDER', _('Experiencias Turísticas')

    name = models.CharField(max_length=255)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tourism_providers')

    # --- Territorial Hierarchy (DIVIPOLA) ---
    department = models.ForeignKey('turismo.Department', on_delete=models.PROTECT, related_name='providers', null=True, blank=True)
    municipality = models.ForeignKey('turismo.Municipality', on_delete=models.PROTECT, related_name='providers', null=True, blank=True)

    location = models.JSONField(default=dict, help_text="Coordenadas y dirección")
    contact = models.JSONField(default=dict, help_text="Teléfonos, redes sociales, etc.")
    status = models.CharField(max_length=20, default='ACTIVE')

    # --- R.N.T. Data ---
    rnt_number = models.CharField(_('Número RNT'), max_length=50, blank=True, null=True, db_index=True)
    rnt_validated = models.BooleanField(default=False)
    rnt_last_sync = models.DateTimeField(null=True, blank=True)

    # --- Classification ---
    sub_classification = models.CharField(_('Subclasificación'), max_length=150, blank=True, null=True)

    # --- Scoring & Visibility ---
    puntuacion_capacitacion = models.PositiveIntegerField(default=0, help_text="Puntaje por asistencia a capacitaciones.")
    puntuacion_verificacion = models.PositiveIntegerField(default=0, help_text="Puntaje por cumplimiento de requisitos legales.")
    puntuacion_resenas = models.PositiveIntegerField(default=0, help_text="Puntaje por reseñas de turistas.")
    puntuacion_total = models.PositiveIntegerField(default=0, db_index=True)

    def recalcular_puntuacion_total(self):
        self.puntuacion_total = (
            self.puntuacion_capacitacion +
            self.puntuacion_verificacion +
            self.puntuacion_resenas
        )
        self.save(update_fields=['puntuacion_total'])

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"

class BusinessProfile(BaseModel):
    provider = models.OneToOneField(TourismProvider, on_delete=models.CASCADE, related_name='business_profile')
    legal_name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50, unique=True)
    business_address = models.CharField(max_length=500)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    bank_account = models.JSONField(default=dict, help_text="Información bancaria para pagos")

    def __str__(self):
        return self.legal_name

class TourismService(BaseModel):
    class ServiceType(models.TextChoices):
        ACCOMMODATION = 'ACCOMMODATION', _('Habitación / Alojamiento')
        TOUR = 'TOUR', _('Tour / Recorrido')
        FOOD = 'FOOD', _('Comida / Gastronomía')
        TRANSPORT = 'TRANSPORT', _('Transporte')
        EXPERIENCE = 'EXPERIENCE', _('Experiencia')
        PRODUCT = 'PRODUCT', _('Producto Físico')

    provider = models.ForeignKey(TourismProvider, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=18, decimal_places=2)
    capacity = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=True)
    delivery_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.provider.name}"

class AccommodationDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='accommodation_detail')
    room_type = models.CharField(max_length=100)
    amenities = models.JSONField(default=list)

class TourDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='tour_detail')
    itinerary = models.JSONField(default=list)
    difficulty = models.CharField(max_length=50)

class FoodDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='food_detail')
    cuisine_type = models.CharField(max_length=100)
    menu_items = models.JSONField(default=list)

class TransportDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='transport_detail')
    vehicle_type = models.CharField(max_length=100)
    plate = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()

class Reservation(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        CONFIRMED = 'CONFIRMED', _('Confirmada')
        CANCELLED = 'CANCELLED', _('Cancelada')
        COMPLETED = 'COMPLETED', _('Completada')

    provider = models.ForeignKey(TourismProvider, on_delete=models.CASCADE, related_name='reservations')
    service = models.ForeignKey(TourismService, on_delete=models.CASCADE, related_name='reservations')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tourism_reservations')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Reserva {self.id} - {self.service.name}"

class ExperienceDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='experience_detail')
    duration_minutes = models.PositiveIntegerField()
    requirements = models.TextField(blank=True)

class ArtisanDetail(models.Model):
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='artisan_detail')
    material = models.CharField(max_length=100)
    technique = models.CharField(max_length=100)

class ServiceReview(BaseModel):
    service = models.ForeignKey(TourismService, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()

class ProviderAnalytics(models.Model):
    provider = models.OneToOneField(TourismProvider, on_delete=models.CASCADE, related_name='analytics')
    total_sales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    reservation_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
