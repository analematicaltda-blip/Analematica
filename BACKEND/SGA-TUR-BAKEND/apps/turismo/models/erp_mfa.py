import uuid
from django.conf import settings
from django.db import models

class ErpLoginChallenge(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    factor=models.ForeignKey('mfa.Authenticator',on_delete=models.SET_NULL,null=True)
    backend=models.CharField(max_length=255)
    binding_digest=models.CharField(max_length=64)
    password_version=models.CharField(max_length=64)
    factor_version=models.CharField(max_length=64)
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField()
    attempts=models.PositiveSmallIntegerField(default=0)
    consumed_at=models.DateTimeField(null=True)

class ErpTotpUsage(models.Model):
    factor=models.OneToOneField('mfa.Authenticator',on_delete=models.CASCADE,primary_key=True)
    last_counter=models.BigIntegerField(default=-1)
    failures=models.PositiveSmallIntegerField(default=0)
    locked_until=models.DateTimeField(null=True)
