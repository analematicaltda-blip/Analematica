"""Personal opt-in and company-primary-administrator access, independent of job roles."""
from dataclasses import dataclass
from datetime import datetime,timedelta
import re
from uuid import UUID
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from ..models import Wallet
PERSONAL_TYPES={'TURISTA','EMPLEADO'}  # Historical storage labels, not a tourism-only eligibility rule.

@dataclass(frozen=True)
class VerifiedCompanyAdministrator:
    user_id: int
    wallet_id: UUID
    company_reference: str
    platform: str
    role: str
    evidence_digest: str
    checked_at: datetime
    valid_until: datetime


def registered_actor(user):
    if not user or not user.is_authenticated or not user.is_active or user.pk is None:raise PermissionDenied('Se requiere una cuenta personal registrada y activa.')


def personal_signup(user):
    registered_actor(user)
    return Wallet.objects.filter(user_id=user.pk,owner_type__in=PERSONAL_TYPES,metadata__wallet_signup=True).exists()


@transaction.atomic
def register_personal_profile(user):
    """Explicit opt-in. No provider account, currency, limits or money is invented."""
    registered_actor(user)
    wallet,created=Wallet.objects.select_for_update().get_or_create(owner_type='TURISTA',owner_id=str(user.pk),defaults={'user_id':user.pk,'estado':Wallet.Status.SUSPENDIDO,'metadata':{'wallet_signup':True}})
    if wallet.user_id!=user.pk:raise PermissionDenied('El registro existente requiere revisión de titularidad.')
    if not created:
        wallet.metadata={**wallet.metadata,'wallet_signup':True};wallet.save(update_fields=['metadata','updated_at'])
    return wallet


def company_access(user,wallet,verifier=None):
    registered_actor(user)
    if wallet.owner_type in PERSONAL_TYPES:return False
    verifier=verifier if verifier is not None else getattr(settings,'WALLET_COMPANY_ADMIN_VERIFIER',None)
    if not callable(verifier):return False
    try:
        proof=verifier(user,wallet);now=timezone.now()
        return (type(proof)is VerifiedCompanyAdministrator and proof.user_id==user.pk and proof.wallet_id==wallet.pk and proof.company_reference==wallet.owner_id and proof.platform in {'ERP_TUR','SGA_CD'} and proof.role=='COMPANY_ADMINISTRATOR' and isinstance(proof.evidence_digest,str) and re.fullmatch('[0-9a-f]{64}',proof.evidence_digest)is not None and isinstance(proof.checked_at,datetime) and isinstance(proof.valid_until,datetime) and timezone.is_aware(proof.checked_at) and timezone.is_aware(proof.valid_until) and now-timedelta(minutes=5)<=proof.checked_at<=now<proof.valid_until<=proof.checked_at+timedelta(minutes=5))
    except Exception:return False


def accessible_wallets(user):
    registered_actor(user)
    personal=Q(user_id=user.pk,owner_type__in=PERSONAL_TYPES) if personal_signup(user) else Q(pk__in=[])
    corporate=[];verifier=getattr(settings,'WALLET_COMPANY_ADMIN_VERIFIER',None)
    # Both discovery and verification are server integrations, never client IDs/headers.
    if callable(verifier) and callable(getattr(verifier,'wallet_ids',None)):
        try:
            ids=verifier.wallet_ids(user)
            if not isinstance(ids,(list,tuple)) or len(ids)>100:raise ValueError()
            ids=[UUID(str(value)) for value in ids]
            corporate=[wallet.pk for wallet in Wallet.objects.filter(pk__in=ids).exclude(owner_type__in=PERSONAL_TYPES) if company_access(user,wallet,verifier)]
        except Exception:corporate=[]
    return Wallet.objects.filter(personal|Q(pk__in=corporate))


def require_wallet_access(user,wallet):
    registered_actor(user)
    allowed=(wallet.user_id==user.pk and personal_signup(user)) if wallet.owner_type in PERSONAL_TYPES else company_access(user,wallet)
    if not allowed:raise PermissionDenied('Solo el titular personal o el administrador verificado de la empresa puede acceder a esta billetera.')
