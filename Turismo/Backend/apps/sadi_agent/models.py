import uuid
from django.conf import settings
from django.db import models
 
from api.models import CustomUser
 

# --- Modelos de Seguridad Voice-First ---

class VoicePermission(models.Model):
    """
    Define los permisos para ejecutar acciones de voz, basado en rol y dominio.
    """
 
    role = models.CharField(
        max_length=50,
        choices=CustomUser.Role.choices,
        help_text="Rol del usuario al que se aplica el permiso."
    )
    domain = models.CharField(
        max_length=100,
        help_text="El dominio de la misión (ej. 'prestadores', 'gubernamental')."
    )
    action = models.CharField(
        max_length=100,
        help_text="La acción específica dentro del dominio (ej. 'crear', 'consultar')."
    )

    class Meta:
        verbose_name = "Permiso de Voz"
        verbose_name_plural = "Permisos de Voz"
        unique_together = ('role', 'domain', 'action')

    def __str__(self):
        return f"Permiso: {self.role} puede '{self.action}' en '{self.domain}'"

# --- Modelos del Motor Semántico ---

class SemanticDomain(models.Model):
    """
    Define un dominio semántico, como 'prestadores' o 'gubernamental'.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Nombre del dominio.")
    description = models.TextField(blank=True, help_text="Descripción del dominio.")

    def __str__(self):
        return self.name

class Intent(models.Model):
    """
    Define una intención, como 'ONBOARDING_PRESTADOR'.
    """
    domain = models.ForeignKey(SemanticDomain, on_delete=models.CASCADE, related_name='intents')
    name = models.CharField(max_length=100, help_text="Nombre de la intención.")
    description = models.TextField(blank=True, help_text="Descripción de la intención.")

    class Meta:
        unique_together = ('domain', 'name')

    def __str__(self):
        return f"{self.domain.name} / {self.name}"

class Entity(models.Model):
    """
    Define una entidad que puede ser extraída de un comando, como 'nombre' o 'email'.
    """
    domain = models.ForeignKey(SemanticDomain, on_delete=models.CASCADE, related_name='entities')
    name = models.CharField(max_length=100, help_text="Nombre de la entidad.")

    class Meta:
        unique_together = ('domain', 'name')

    def __str__(self):
        return f"{self.domain.name} / {self.name}"

class Example(models.Model):
    """
    Un ejemplo de un comando de voz para entrenar al motor semántico.
    """
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField(unique=True, help_text="Texto del comando de ejemplo.")
    language = models.CharField(max_length=10, default='es', help_text="Idioma del ejemplo (ej. 'es', 'en').")
 

    def __str__(self):
        return f"Ejemplo para '{self.intent.name}': '{self.text}'"

# --- Modelo de Auditoría ---

class VoiceInteractionLog(models.Model):
    """
    Registra cada interacción de voz de extremo a extremo para auditoría.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='voice_interactions')
    timestamp_start = models.DateTimeField(auto_now_add=True)
    timestamp_end = models.DateTimeField(null=True, blank=True)

    # Datos de entrada
    audio_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash del archivo de audio de entrada.")
    detected_language = models.CharField(max_length=10, blank=True)
    transcribed_text = models.TextField(blank=True)
    normalized_text = models.TextField(blank=True, help_text="Texto traducido al idioma base (español).")

    # Procesamiento
    detected_intent = models.ForeignKey(Intent, on_delete=models.SET_NULL, null=True, blank=True)
    extracted_entities = models.JSONField(null=True, blank=True)

    # Seguridad
    permission_checked = models.BooleanField(default=False)
    permission_granted = models.BooleanField(default=False)

    # Resultado
    mission_id = models.UUIDField(null=True, blank=True, help_text="ID de la misión de SARITA si fue creada.")
    final_status = models.CharField(max_length=50, default="PENDING") # PENDING, REJECTED, COMPLETED, FAILED
    text_response = models.TextField(blank=True)

    class Meta:
 
        verbose_name = "Registro de Interacción por Voz"
        verbose_name_plural = "Registros de Interacción por Voz"
        ordering = ['-timestamp_start']

    def __str__(self):
        return f"Interacción de {self.user} a las {self.timestamp_start.strftime('%Y-%m-%d %H:%M')}"
 
