"""Minimal local security audit; SQL/operator controls are required for stronger immutability."""
import uuid
from django.db import models


class SecurityEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError('Security events cannot be updated through the application.')

    def delete(self):
        raise ValueError('Security events require an explicit retention procedure.')


class ErpSecurityEvent(models.Model):
    class Kind(models.TextChoices):
        RECOVERY_ISSUED='recovery_issued'
        RECOVERY_ROTATED='recovery_rotated'
        PASSWORD_RESET='password_reset'
        RECOVERY_USED='recovery_used'

    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    # No cascading FK: deleting an account/factor must not erase its audit trail.
    actor_id=models.PositiveBigIntegerField(db_index=True)
    kind=models.CharField(max_length=32,choices=Kind.choices)
    occurred_at=models.DateTimeField(auto_now_add=True,db_index=True)
    challenge_id=models.UUIDField(null=True)
    factor_id=models.PositiveBigIntegerField(null=True)
    objects=SecurityEventQuerySet.as_manager()

    def save(self,*args,**kwargs):
        if not self._state.adding:raise ValueError('Security events are append-only in the application.')
        return super().save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        raise ValueError('Security events require an explicit retention procedure.')
