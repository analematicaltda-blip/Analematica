"""Append-only reviewed account classifications; never balances or payment orders."""
from django.conf import settings
from django.db import models
from apps.core_erp.base_models import BaseErpModel

class AccountingRatioPolicy(BaseErpModel):
    tenant=models.ForeignKey('core_erp.Tenant',on_delete=models.PROTECT)
    revision=models.PositiveIntegerField()
    mapping=models.JSONField()
    evidence_digest=models.CharField(max_length=64)
    reviewer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    digest=models.CharField(max_length=64)

    class Meta:
        app_label='core_erp'
        constraints=[models.UniqueConstraint(fields=['tenant','revision'],name='accounting_ratio_revision_once')]

    def save(self,*args,**kwargs):
        if not self._state.adding or kwargs.get('force_update') or kwargs.get('update_fields'):
            raise PermissionError('Create a reviewed revision instead of editing history.')
        # An object reconstructed with an existing UUID must never become an UPDATE.
        kwargs['force_insert']=True
        return super().save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        raise PermissionError('Reviewed ratio policies are historical records.')
