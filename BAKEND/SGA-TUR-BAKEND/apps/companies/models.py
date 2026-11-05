from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
import uuid

class Company(models.Model):
    """
    Representa una empresa cliente (inquilino) en el sistema.
    Cada compañía opera en un silo de datos lógico separado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Nombre legal y completo de la empresa cliente."
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Código corto y único usado en la codificación de documentos (ej. SNT, TRVW)."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la suscripción de la compañía está activa. Desmarcar para suspender el acceso."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'companies'
        verbose_name = "Company (Tenant)"
        verbose_name_plural = "Companies (Tenants)"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class CompanyEncryptionKey(models.Model):
    """
    Almacena los secretos criptográficos para una compañía específica.
    Este modelo es fundamental para la seguridad de 'conocimiento cero'.
    La existencia de este registro está garantizada por una señal de Django.
    """
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        primary_key=True, # La clave primaria de este modelo es la misma que la de Company
        related_name='encryption_key'
    )
    # La 'sal' es una cadena aleatoria y única que se mezcla con otros secretos
    # para derivar la clave de cifrado.
    key_salt = models.CharField(
        max_length=255,
        unique=True,
        help_text="Sal criptográfica única generada para la derivación de claves."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encryption Key for {self.company.name}"

# --- SEÑALES (SIGNALS) - Automatización a nivel de base de datos ---
@receiver(post_save, sender=Company)
def create_company_encryption_key(sender, instance, created, **kwargs):
    """
    Una señal que se dispara automáticamente después de que un objeto Company es guardado.
    Si la compañía es nueva (created=True), crea una CompanyEncryptionKey asociada
    con una 'sal' aleatoria, garantizando que cada compañía tenga su material criptográfico.
    """
    if created:
        # Genera una 'sal' criptográficamente segura.
        salt = get_random_string(128)
        CompanyEncryptionKey.objects.create(company=instance, key_salt=salt)
