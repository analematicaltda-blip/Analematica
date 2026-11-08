import uuid
from django.conf import settings
from django.db import models

class ErpTotpEnrollment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    binding_digest=models.CharField(max_length=64)
    password_version=models.CharField(max_length=64)
    factor_version=models.CharField(max_length=64)
    sealed_secret=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField()
    attempts=models.PositiveSmallIntegerField(default=0)
    consumed_at=models.DateTimeField(null=True)
