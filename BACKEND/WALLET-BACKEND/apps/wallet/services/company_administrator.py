"""Opt-in ERP-TUR adapter. SGA-CD's distinct identity store is not inferred."""
from datetime import timedelta
from django.utils import timezone
from apps.turismo.models import VerifiedCompanyLink
from apps.turismo.services.company_identity import resolve_company
from .access_policy import VerifiedCompanyAdministrator

class TourismCompanyAdministrator:
    def wallet_ids(self,user):
        from ..models import Wallet
        tenant_ids=list(VerifiedCompanyLink.objects.filter(administrator_id=user.pk,revoked_at__isnull=True,valid_until__gt=timezone.now()).values_list('tenant_id',flat=True)[:101])
        if len(tenant_ids)>100:return []
        return list(Wallet.objects.filter(owner_type='CORPORATIVO',owner_id__in=[str(value) for value in tenant_ids]).values_list('pk',flat=True)[:100])
    def __call__(self,user,wallet):
        if wallet.owner_type!='CORPORATIVO':return None
        link=VerifiedCompanyLink.objects.filter(tenant_id=wallet.owner_id).first()
        if link is None:return None
        link=resolve_company(user,link.provider_id)
        now=timezone.now()
        return VerifiedCompanyAdministrator(user_id=user.pk,wallet_id=wallet.pk,company_reference=str(link.tenant_id),platform='ERP_TUR',role='COMPANY_ADMINISTRATOR',evidence_digest=link.evidence_digest,checked_at=now,valid_until=min(now+timedelta(minutes=5),link.valid_until))
