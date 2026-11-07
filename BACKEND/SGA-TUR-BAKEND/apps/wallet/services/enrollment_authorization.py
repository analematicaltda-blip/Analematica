"""Independent account authorization, purpose-bound and short-lived.

Issuance has NO HTTP endpoint and requires a trusted server identity adapter.
A password/session, device biometric flag or hardware attestation alone is NOT
account recovery. No private key or document recovery is performed here.
"""
from dataclasses import dataclass
from datetime import datetime,timedelta
import hashlib
import re
from uuid import UUID
from django.conf import settings
from django.core import signing
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from ..models import WalletDeviceCredential
from .wallet_service import WalletOperationUnavailable
SALT='sgacd.wallet.independent-enrollment.v1'

@dataclass(frozen=True)
class IndependentEnrollmentApproval:
    approval_id: UUID
    user_id: int
    credential_id: UUID
    audience: UUID
    public_key_hash: str
    nonce_hash: str
    method: str
    evidence_hash: str
    checked_at: datetime
    valid_until: datetime
    replaces_id: UUID | None=None


@transaction.atomic
def authorize_enrollment(user,credential_id,public_key,reference,replaces_id=None):
    """For a server workflow after a verified passkey/recovery review, not request JSON."""
    from .device_approvals import actor,audience,raw_public_key
    actor(user)
    if not getattr(settings,'WALLET_DEVICE_ENROLLMENT_ENABLED',False):raise WalletOperationUnavailable('El alta de dispositivos no está habilitada.')
    verifier=getattr(settings,'WALLET_ENROLLMENT_IDENTITY_VERIFIER',None)
    if not callable(verifier):raise WalletOperationUnavailable('Falta un verificador independiente de identidad para el alta o recuperación.')
    if not isinstance(reference,str) or not 1<=len(reference)<=128:raise PermissionDenied('Referencia de verificación inválida.')
    credential=get_object_or_404(WalletDeviceCredential.objects.select_for_update(),id=credential_id,user_id=user.pk)
    now=timezone.now()
    if credential.status!='PENDING' or credential.audience!=audience() or credential.enrollment_expires_at<=now:raise PermissionDenied('Alta inválida o vencida.')
    raw,_=raw_public_key(public_key);key_hash=hashlib.sha256(raw).hexdigest()
    if replaces_id is not None:
        old=get_object_or_404(WalletDeviceCredential,id=replaces_id,user_id=user.pk,audience=credential.audience)
        if old.status not in {'VERIFIED','REVOKED'}:raise PermissionDenied('La credencial anterior no corresponde a un dispositivo registrado.')
        if old.pk==credential.pk:raise PermissionDenied('No se puede reemplazar la misma credencial.')
        replaces_id=old.pk
    try:evidence=verifier(user,credential,raw,reference,replaces_id)
    except PermissionDenied:raise PermissionDenied('No se verificó la autorización independiente de identidad.') from None
    except Exception:raise WalletOperationUnavailable('No se pudo verificar la identidad. El dispositivo continúa pendiente.') from None
    if type(evidence)is not IndependentEnrollmentApproval or not isinstance(evidence.approval_id,UUID) or evidence.user_id!=user.pk or evidence.credential_id!=credential.pk or evidence.audience!=credential.audience or evidence.public_key_hash!=key_hash or evidence.nonce_hash!=credential.enrollment_nonce_hash or evidence.replaces_id!=replaces_id or evidence.method not in {'WEBAUTHN_UV','REVIEWED_RECOVERY'} or not isinstance(evidence.evidence_hash,str) or re.fullmatch('[0-9a-f]{64}',evidence.evidence_hash) is None:raise PermissionDenied('La verificación independiente no acredita esta cuenta, llave y alta.')
    if not isinstance(evidence.checked_at,datetime) or not isinstance(evidence.valid_until,datetime) or not timezone.is_aware(evidence.checked_at) or not timezone.is_aware(evidence.valid_until) or not now-timedelta(minutes=5)<=evidence.checked_at<=now or not now<evidence.valid_until<=min(now+timedelta(minutes=5),credential.enrollment_expires_at):raise PermissionDenied('Verificación de identidad vencida.')
    claims={'purpose':'DEVICE_ENROLLMENT_V1','approval':str(evidence.approval_id),'user':user.pk,'credential':str(credential.pk),'audience':str(credential.audience),'key':key_hash,'nonce':credential.enrollment_nonce_hash,'method':evidence.method,'evidence':evidence.evidence_hash,'until':int(evidence.valid_until.timestamp()),'replaces':str(replaces_id) if replaces_id else None}
    return signing.dumps(claims,salt=SALT,compress=False)


def verify_authorization(user,credential,public_key,token):
    if not isinstance(token,str) or not 1<=len(token)<=4096:raise PermissionDenied('Falta la autorización independiente de alta o recuperación.')
    try:claims=signing.loads(token,salt=SALT,max_age=300)
    except (signing.BadSignature,ValueError,TypeError):raise PermissionDenied('Autorización de alta inválida o vencida.')
    expected={'purpose','approval','user','credential','audience','key','nonce','method','evidence','until','replaces'}
    if not isinstance(claims,dict) or set(claims)!=expected or claims['purpose']!='DEVICE_ENROLLMENT_V1' or claims['user']!=user.pk or claims['credential']!=str(credential.pk) or claims['audience']!=str(credential.audience) or claims['nonce']!=credential.enrollment_nonce_hash or claims['key']!=hashlib.sha256(public_key).hexdigest() or claims['method'] not in {'WEBAUTHN_UV','REVIEWED_RECOVERY'} or type(claims['until'])is not int or claims['until']<=int(timezone.now().timestamp()):raise PermissionDenied('La autorización no corresponde a esta alta y llave.')
    return claims
