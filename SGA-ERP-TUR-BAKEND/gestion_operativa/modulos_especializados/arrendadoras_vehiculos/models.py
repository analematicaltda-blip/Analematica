# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/arrendadoras_vehiculos/models.py
from django.db import models
from django.conf import settings
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

class VehiculoDeAlquiler(models.Model):
    """
    Representa un vehículo específico disponible para alquilar.
    Hereda la lógica de un producto/servicio genérico pero con campos especializados.
    """
    CATEGORIA_CHOICES = [
        ('economico', 'Económico'),
        ('compacto', 'Compacto'),
        ('intermedio', 'Intermedio'),
        ('suv', 'SUV'),
        ('lujo', 'Lujo'),
        ('van', 'Van/Minivan'),
        ('moto', 'Motocicleta'),
    ]
    TRANSMISION_CHOICES = [
        ('automatica', 'Automática'),
        ('manual', 'Manual'),
    ]

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='vehiculos_de_alquiler')
    nombre = models.CharField(max_length=100, help_text="Ej: Toyota Corolla 2023")
    placa = models.CharField(max_length=10, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='compacto')
    transmision = models.CharField(max_length=10, choices=TRANSMISION_CHOICES, default='automatica')
    numero_pasajeros = models.PositiveIntegerField(default=5)
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)

    # Podríamos añadir más detalles como imagen, características (aire acondicionado, etc.)
    # imagen = models.ImageField(upload_to='vehiculos_alquiler/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.placa}) - {'Disponible' if self.disponible else 'No Disponible'}"

class Alquiler(models.Model):
    """
    Representa el registro de un alquiler de un vehículo.
    """
    ESTADO_ALQUILER_CHOICES = [
        ('reservado', 'Reservado'),
        ('activo', 'Activo'), # El cliente ya recogió el vehículo
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    vehiculo = models.ForeignKey(VehiculoDeAlquiler, on_delete=models.PROTECT, related_name='alquileres')
    # cliente = models.ForeignKey('gestion_comercial.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente_temporal = models.CharField(max_length=150)
    email_cliente = models.EmailField()

    fecha_recogida = models.DateTimeField()
    fecha_devolucion = models.DateTimeField()

    costo_total_calculado = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_ALQUILER_CHOICES, default='reservado')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calcular el costo total basado en los días de alquiler
        duracion = self.fecha_devolucion - self.fecha_recogida
        dias_alquiler = duracion.days + (1 if duracion.seconds > 0 else 0) # Redondea hacia arriba
        if dias_alquiler <= 0:
            dias_alquiler = 1 # Mínimo 1 día de alquiler

        self.costo_total_calculado = self.vehiculo.precio_por_dia * dias_alquiler

        # Al guardar, se podría cambiar el estado del vehículo a no disponible si el alquiler está activo
        # Esta lógica puede ser más compleja (ej. verificar solapamiento de fechas)
        if self.estado == 'activo':
            self.vehiculo.disponible = False
            self.vehiculo.save()
        elif self.estado in ['finalizado', 'cancelado'] and not self.vehiculo.disponible:
             # Solo lo vuelve disponible si este era el alquiler que lo bloqueaba.
             # Ojo: Una lógica más robusta verificaría si hay otros alquileres activos para este vehículo.
            self.vehiculo.disponible = True
            self.vehiculo.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Alquiler de {self.vehiculo.nombre} a {self.nombre_cliente_temporal} desde {self.fecha_recogida.strftime('%Y-%m-%d')}"
