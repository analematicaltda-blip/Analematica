import uuid
from django.conf import settings
from django.db import models

class AvailabilityHold(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    provider=models.ForeignKey('turismo.TourismProvider',on_delete=models.PROTECT)
    service=models.ForeignKey('turismo.TourismService',on_delete=models.PROTECT,related_name='capacity_holds')
    requested_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    idempotency_key=models.UUIDField()
    request_digest=models.CharField(max_length=64)
    start_at=models.DateTimeField()
    end_at=models.DateTimeField()
    quantity=models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField()
    released_at=models.DateTimeField(null=True)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['provider','requested_by','idempotency_key'],name='unique_availability_hold_request'),models.CheckConstraint(condition=models.Q(quantity__gt=0),name='positive_hold_quantity'),models.CheckConstraint(condition=models.Q(end_at__gt=models.F('start_at')),name='ordered_hold_interval')]
        indexes=[models.Index(fields=['service','expires_at'],name='hold_service_expiry_idx')]
