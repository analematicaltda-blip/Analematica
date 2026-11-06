from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ...modulos_genericos.productos_servicios.models import Product

# El Restaurante principal, vinculado al perfil del prestador
class Restaurante(models.Model):
    perfil = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name='restaurante')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    ofrece_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

# Menú del restaurante (ej. Almuerzo, Cena)
class Menu(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='menus')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Menú '{self.nombre}' de {self.restaurante.nombre}"

# Categoría dentro de un menú (ej. Entradas, Platos Fuertes, Postres)
class CategoriaPlato(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el menú")

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

# Un plato específico del menú
class Plato(models.Model):
    categoria = models.ForeignKey(CategoriaPlato, on_delete=models.CASCADE, related_name='platos')
    # Reutilizamos el modelo de Producto para estandarizar
    producto = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='plato')
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.producto.nombre

# Zonas de entrega para el servicio de delivery
class ZonaDelivery(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='zonas_delivery')
    nombre = models.CharField(max_length=100, help_text="Ej: 'Centro', 'Zona Norte'")
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_estimado_minutos = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Zona: {self.nombre} ({self.restaurante.nombre})"
