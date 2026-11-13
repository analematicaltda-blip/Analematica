"""One-use hardware-key approval challenges. Client biometric booleans are never proof.

Vendor attestation verification is a trusted server integration, disabled until an
operator configures a real verifier. No software-key enrollment fallback exists.
"""
import base64
import hashlib
import hmac
import secrets
import re
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime,timedelta
from uuid import UUID
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError,Throttled
from ..models import WalletDeviceCredential,WalletDeviceChallenge,WalletTransferIntent
from .wallet_service import WalletOperationUnavailable

@dataclass(frozen=True)
class VerifiedAttestation:
    """Only a configured, trusted verifier may construct this result, never request JSON."""
    credential_id: UUID
    user_id: int
    audience: UUID
    public_key: bytes
    nonce_hash: str
    valid_until: datetime
    hardware_biometric: bool
    platform: str = ""
    policy_digest: str = ""
    certificate_serials: tuple = ()


@lru_cache(maxsize=4)
def _load_configured_verifier(path):
    from .attestation_config import load_android_verifier
    return load_android_verifier(path)


def configured_verifier():
    explicit=getattr(settings,'WALLET_ATTESTATION_VERIFIER',None)
    if explicit is not None:return explicit
    path=getattr(settings,'WALLET_ANDROID_ATTESTATION_POLICY_FILE','')
    if not path:return None
    try:return _load_configured_verifier(path)
    except Exception:raise WalletOperationUnavailable('La política de atestación no está disponible o no es válida.')


def audience():
    try:return UUID(str(settings.WALLET_APPROVAL_AUDIENCE))
    except (AttributeError,TypeError,ValueError):raise WalletOperationUnavailable('Configure la identidad estable del servicio de autorizaciones.')


def actor(user):
    from .access_policy import registered_actor
    registered_actor(user)


def raw_public_key(value):
    try:
        if not isinstance(value,str) or len(value)>128:raise ValueError()
        raw=base64.b64decode(value,validate=True)
        if len(raw)!=65 or raw[0]!=4:raise ValueError()
        key=ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(),raw)
        return raw,key
    except (ValueError,TypeError):raise ValidationError('Llave pública P-256 inválida.')


@transaction.atomic
def begin_enrollment(user):
    actor(user)
    if not getattr(settings,'WALLET_DEVICE_ENROLLMENT_ENABLED',False):raise WalletOperationUnavailable('El alta de dispositivos no está habilitada.')
    now=timezone.now()
    if WalletDeviceCredential.objects.filter(user_id=user.pk,status='PENDING',enrollment_expires_at__gt=now).count()>=5:raise Throttled(wait=300)
    nonce=secrets.token_bytes(32)
    credential=WalletDeviceCredential.objects.create(user_id=user.pk,audience=audience(),enrollment_nonce_hash=hashlib.sha256(nonce).hexdigest(),enrollment_expires_at=now+timedelta(minutes=5))
    return credential,base64.b64encode(nonce).decode('ascii')


@transaction.atomic
def attest(user,credential_id,public_key,chain,enrollment_authorization=None):
    actor(user)
    if not getattr(settings,'WALLET_DEVICE_ENROLLMENT_ENABLED',False):raise WalletOperationUnavailable('El alta de dispositivos no está habilitada.')
    credential=get_object_or_404(WalletDeviceCredential.objects.select_for_update(),id=credential_id,user_id=user.pk)
    now=timezone.now()
    if credential.status!='PENDING' or credential.enrollment_expires_at<=now or credential.audience!=audience():raise PermissionDenied('Alta inválida o vencida.')
    verifier=configured_verifier()
    if not callable(verifier):raise WalletOperationUnavailable('Falta un verificador de atestación de hardware validado. El dispositivo continúa pendiente.')
    raw,_=raw_public_key(public_key)
    try:
        if not isinstance(chain,(list,tuple)) or not 1<=len(chain)<=8 or any(not isinstance(cert,str) or len(cert)>24000 for cert in chain):raise ValueError()
        certificates=tuple(base64.b64decode(cert,validate=True) for cert in chain)
        if any(not cert or len(cert)>16384 for cert in certificates):raise ValueError()
    except (ValueError,TypeError):raise ValidationError('Cadena de atestación inválida.')
    from .enrollment_authorization import verify_authorization
    authorization=verify_authorization(user,credential,raw,enrollment_authorization)
    # Configuration-only adapter: must validate vendor roots, nonce, verified boot,
    # package/signing identity, key and biometric policy before returning evidence.
    from .android_attestation import AttestationRejected
    try:evidence=verifier(credential,raw,certificates)
    except AttestationRejected:raise PermissionDenied('La atestación no cumple la política de seguridad.')
    except Exception:raise WalletOperationUnavailable('No se pudo verificar la atestación. El dispositivo continúa pendiente.')
    if type(evidence) is not VerifiedAttestation or evidence.hardware_biometric is not True or evidence.credential_id!=credential.pk or evidence.user_id!=user.pk or evidence.audience!=credential.audience or evidence.public_key!=raw or not isinstance(evidence.nonce_hash,str) or not hmac.compare_digest(evidence.nonce_hash,credential.enrollment_nonce_hash):
        raise PermissionDenied('La evidencia no acredita este dispositivo y solicitante.')
    if not isinstance(evidence.valid_until,datetime) or not timezone.is_aware(evidence.valid_until) or not now<evidence.valid_until<=now+timedelta(days=7):raise PermissionDenied('Vigencia de atestación inválida.')
    if evidence.platform!='ANDROID_KEY_ATTESTATION' or not isinstance(evidence.policy_digest,str) or re.fullmatch('[0-9a-f]{64}',evidence.policy_digest) is None or not isinstance(evidence.certificate_serials,tuple) or not 2<=len(evidence.certificate_serials)<=8 or any(not isinstance(serial,str) or re.fullmatch('[1-9a-f][0-9a-f]{0,39}',serial) is None for serial in evidence.certificate_serials):raise PermissionDenied('Evidencia de confianza incompleta.')
    credential.attestation_platform=evidence.platform;credential.attestation_policy_digest=evidence.policy_digest;credential.attestation_serials=list(evidence.certificate_serials)
    credential.enrollment_authorization_digest=hashlib.sha256(enrollment_authorization.encode()).hexdigest();credential.enrollment_method=authorization['method']
    if authorization['replaces']:
        old=get_object_or_404(WalletDeviceCredential.objects.select_for_update(),id=authorization['replaces'],user_id=user.pk,audience=credential.audience)
        if old.pk==credential.pk:raise PermissionDenied('Reemplazo inválido.')
        old.status='REVOKED';old.revoked_at=now;old.save(update_fields=['status','revoked_at'])
        WalletDeviceChallenge.objects.filter(credential=old,consumed_at__isnull=True,invalidated_at__isnull=True).update(invalidated_at=now)
        credential.replaces=old
    credential.public_key=public_key;credential.status='VERIFIED';credential.verified_at=now;credential.valid_until=evidence.valid_until
    credential.attestation_digest=hashlib.sha256(b''.join(len(cert).to_bytes(4,'big')+cert for cert in certificates)).hexdigest()
    credential.save(update_fields=['public_key','status','verified_at','valid_until','attestation_digest','attestation_platform','attestation_policy_digest','attestation_serials','enrollment_authorization_digest','enrollment_method','replaces'])
    return credential


def active_device(user,credential_id):
    device=get_object_or_404(WalletDeviceCredential.objects.select_for_update(),id=credential_id,user_id=user.pk)
    if device.status!='VERIFIED' or device.audience!=audience() or device.valid_until is None or device.valid_until<=timezone.now():raise PermissionDenied('Dispositivo no verificado, vencido o revocado.')
    verifier=configured_verifier()
    if not callable(getattr(verifier,'check_registered',None)):raise WalletOperationUnavailable('Falta la revisión vigente de confianza del dispositivo.')
    from .android_attestation import AttestationRejected
    try:verifier.check_registered(device)
    except AttestationRejected:raise PermissionDenied('Dispositivo sin confianza vigente o certificado revocado.')
    except Exception:raise WalletOperationUnavailable('No se pudo revisar la confianza vigente del dispositivo.')
    return device


def payload(challenge,intent):
    lines=['SGACD-WALLET-APPROVAL-V1',str(challenge.credential.audience),str(intent.requested_by_id),str(challenge.credential_id),str(intent.pk),str(challenge.pk),challenge.phase,challenge.nonce,intent.digest,str(intent.source_id),str(intent.destination_id),format(intent.amount,'.2f'),intent.currency,str(int(challenge.expires_at.timestamp()))]
    return ('\n'.join(lines)+'\n').encode('ascii')


@transaction.atomic
def issue(user,intent_id,credential_id,phase):
    from .internal_transfer import principal,owned_intent
    principal(user)
    intent=get_object_or_404(WalletTransferIntent.objects.select_for_update(),id=intent_id,requested_by_id=user.pk)
    owned_intent(user,intent.pk,intent.digest)
    device=active_device(user,credential_id)
    expected={'REVIEW':'PENDING','EXECUTE':'REVIEWED'}.get(phase)
    if expected is None or intent.state!=expected or intent.expires_at<=timezone.now():raise PermissionDenied('Etapa inválida o vencida.')
    if phase=='EXECUTE' and intent.review_device_id!=device.pk:raise PermissionDenied('Las dos autorizaciones deben corresponder al mismo dispositivo del solicitante.')
    WalletDeviceChallenge.objects.filter(intent=intent,phase=phase,consumed_at__isnull=True,invalidated_at__isnull=True).update(invalidated_at=timezone.now())
    challenge=WalletDeviceChallenge.objects.create(credential=device,intent=intent,phase=phase,nonce=base64.b64encode(secrets.token_bytes(32)).decode('ascii'),expires_at=min(intent.expires_at,timezone.now()+timedelta(minutes=2)))
    return challenge,payload(challenge,intent)


def consume(user,intent,phase,proof):
    """Called only inside the same transaction as the review or balance updates."""
    if not isinstance(proof,dict) or set(proof)!={'challenge','signature'}:raise PermissionDenied('Falta una autorización firmada del dispositivo.')
    challenge=get_object_or_404(WalletDeviceChallenge,id=proof['challenge'],intent=intent,credential__user_id=user.pk)
    device=active_device(user,challenge.credential_id)
    challenge=get_object_or_404(WalletDeviceChallenge.objects.select_for_update(),pk=challenge.pk)
    if challenge.phase!=phase or challenge.consumed_at is not None or challenge.invalidated_at is not None or challenge.expires_at<=timezone.now():raise PermissionDenied('Desafío usado, reemplazado, vencido o de otra etapa.')
    if phase=='EXECUTE' and intent.review_device_id!=device.pk:raise PermissionDenied('El dispositivo de la segunda autorización cambió.')
    try:
        if not isinstance(proof['signature'],str) or len(proof['signature'])>128:raise ValueError()
        signature=base64.b64decode(proof['signature'],validate=True)
        if not 8<=len(signature)<=80:raise ValueError()
        _,key=raw_public_key(device.public_key)
        key.verify(signature,payload(challenge,intent),ec.ECDSA(hashes.SHA256()))
    except (InvalidSignature,ValueError,TypeError):raise PermissionDenied('Firma de autorización inválida.')
    if WalletDeviceChallenge.objects.filter(pk=challenge.pk,consumed_at__isnull=True,invalidated_at__isnull=True).update(consumed_at=timezone.now())!=1:raise PermissionDenied('El desafío ya se utilizó.')
    return device


@transaction.atomic
def revoke(user,credential_id):
    actor(user)
    device=get_object_or_404(WalletDeviceCredential.objects.select_for_update(),id=credential_id,user_id=user.pk)
    device.status='REVOKED';device.revoked_at=timezone.now();device.save(update_fields=['status','revoked_at'])
    WalletDeviceChallenge.objects.filter(credential=device,consumed_at__isnull=True,invalidated_at__isnull=True).update(invalidated_at=timezone.now())
    return device
