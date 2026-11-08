"""Operator-reviewed identity bridge; never inferred from request tenant headers."""
import uuid
from django.conf import settings
from django.db import models

class VerifiedCompanyLink(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    provider = models.OneToOneField('turismo.TourismProvider',on_delete=models.PROTECT,related_name='verified_company_link')
    tenant = models.OneToOneField('core_erp.Tenant',on_delete=models.PROTECT,related_name='verified_tourism_link')
    administrator = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='verified_company_administrations')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='reviewed_company_links')
    verified_tax_id = models.CharField(max_length=50)
    evidence_digest = models.CharField(max_length=64)
    verified_at = models.DateTimeField()
    valid_until = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
