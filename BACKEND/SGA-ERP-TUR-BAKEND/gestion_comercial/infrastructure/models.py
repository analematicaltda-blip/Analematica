# infrastructure/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='comercial_users', null=True, blank=True)
    roles = models.ManyToManyField(Role, related_name='comercial_users', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='comercial_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='comercial_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# --- Modelos para el Arquitecto de Embudos ---

class ComercialCategoria(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class ComercialSubcategoria(models.Model):
    categoria = models.ForeignKey(ComercialCategoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"

class LandingPage(models.Model):
    subcategoria = models.ForeignKey(ComercialSubcategoria, on_delete=models.CASCADE, related_name='landing_pages')
    slug = models.SlugField(unique=True)
    estado = models.CharField(max_length=10, choices=[('borrador', 'Borrador'), ('publicado', 'Publicado')], default='borrador')
    def __str__(self):
        return self.slug

class Embudo(models.Model):
    landing_page = models.OneToOneField(LandingPage, on_delete=models.CASCADE, related_name='embudo')
    nombre = models.CharField(max_length=255)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.nombre

class Pagina(models.Model):
    embudo = models.ForeignKey(Embudo, on_delete=models.CASCADE, related_name='paginas')
    tipo = models.CharField(max_length=50)
    orden = models.PositiveIntegerField()
    history = HistoricalRecords()
    class Meta:
        ordering = ['orden']
    def __str__(self):
        return f"Página tipo {self.tipo} en {self.embudo.nombre}"

class Bloque(models.Model):
    pagina = models.ForeignKey(Pagina, on_delete=models.CASCADE, related_name='bloques')
    tipo = models.CharField(max_length=50)
    orden = models.PositiveIntegerField()
    config_json = models.JSONField()
    history = HistoricalRecords()
    class Meta:
        ordering = ['orden']
    def __str__(self):
        return f"Bloque tipo {self.tipo} en página {self.pagina.id}"

# --- Modelos para el Módulo de IA y Trazabilidad ---

class AIInteraction(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='ai_interactions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_interactions')
    proveedor_usado = models.CharField(max_length=100)
    prompt_original = models.TextField()
    resultado = models.TextField(blank=True)
    errores = models.TextField(blank=True)
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Interaction {self.id} by {self.user.username if self.user else 'System'}"

class ContentAsset(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='content_assets')
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    asset_type = models.CharField(max_length=50, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')])
    content = models.TextField() # Para texto o URLs
    # campaign = models.ForeignKey('Campaign', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset_type.capitalize()} Asset {self.id}"

class AsyncTask(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='async_tasks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='async_tasks')
    task_type = models.CharField(max_length=100) # ej. 'video_generation'
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')])
    result_url = models.URLField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.id} ({self.task_type}) - {self.status}"
 