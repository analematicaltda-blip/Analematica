"""Immutable non-binding commercial drafts; never a payment or tax document."""
import uuid
from django.conf import settings
from django.db import models

class QuotationDraft(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    provider = models.ForeignKey('turismo.TourismProvider',on_delete=models.PROTECT,related_name='quotation_drafts')
    tenant = models.ForeignKey('core_erp.Tenant',on_delete=models.PROTECT,related_name='quotation_drafts')
    customer = models.ForeignKey('mi_negocio.Cliente',on_delete=models.PROTECT,related_name='quotation_drafts')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='quotation_drafts')
    idempotency_key = models.UUIDField()
    request_digest = models.CharField(max_length=64)
    snapshot = models.JSONField()
    snapshot_digest = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    withdrawn_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['provider','requested_by','idempotency_key'],name='quotation_request_once')]
