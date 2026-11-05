from apps.domain_business.operativa.models import ProviderProfile as DomainProviderProfile
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

# Proxy or Redirection
class ProviderProfile(DomainProviderProfile):
    class Meta:
        proxy = True

class TenantAwareModel(BaseModel):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="%(class)s_items", null=True, blank=True)

    class Meta(BaseModel.Meta):
        abstract = True

class CategoriaPrestador(BaseModel):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
