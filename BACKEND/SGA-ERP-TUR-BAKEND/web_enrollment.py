"""Two-step first-factor enrollment. Existing authenticators are never replaced."""
import hashlib,hmac,secrets,time
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model,BACKEND_SESSION_KEY
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from allauth.mfa.models import Authenticator
from allauth.mfa import app_settings
from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret,hotp_value,format_hotp_value
from apps.common.mfa_adapter import EncryptedMFAAdapter
from apps.turismo.models import ErpTotpEnrollment,ErpTotpUsage
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied
from .web_mfa import enrollment_version,totp_secret


def actor(request):
    user=get_user_model().objects.select_for_update().get(pk=request.user.pk)
    if not user.is_active or getattr(user,'is_agent',False):raise PermissionDenied('Se requiere una cuenta personal activa.')
    return user


def finish(proposal):
    proposal.consumed_at=timezone.now();proposal.sealed_secret='';proposal.save(update_fields=['consumed_at','sealed_secret'])


def bound(request,proposal):
    data=request.session.get('erp_totp_enrollment')
    return isinstance(data,dict) and data.get('id')==str(proposal.pk) and isinstance(data.get('binding'),str) and hmac.compare_digest(hashlib.sha256(data['binding'].encode()).hexdigest(),proposal.binding_digest)


@transaction.atomic
def start(request,password):
    user=actor(request)
    if not isinstance(password,str) or not 1<=len(password)<=1024 or not check_password(password,user.password):raise AuthenticationFailed('Contraseña no válida.')
    version,factors=enrollment_version(user)
    if factors:raise PermissionDenied('La cuenta ya tiene factores registrados. Este proceso no permite sustituirlos.')
    if app_settings.TOTP_DIGITS not in (6,8) or app_settings.TOTP_PERIOD!=30 or getattr(settings,'MFA_TOTP_INSECURE_BYPASS_CODE',None):raise PermissionDenied('La configuración de verificación requiere revisión.')
    if request.session.get(BACKEND_SESSION_KEY) not in settings.AUTHENTICATION_BACKENDS:raise PermissionDenied('Reinicia tu sesión antes de continuar.')
    previous=request.session.get('erp_totp_enrollment')
    if isinstance(previous,dict):
        try:
            old=ErpTotpEnrollment.objects.select_for_update().filter(pk=previous.get('id'),user=user,consumed_at__isnull=True).first()
            if old and bound(request,old):finish(old)
        except (ValueError,TypeError,ValidationError):pass
    secret=generate_totp_secret();binding=secrets.token_urlsafe(32)
    proposal=ErpTotpEnrollment.objects.create(user=user,binding_digest=hashlib.sha256(binding.encode()).hexdigest(),password_version=user.get_session_auth_hash(),factor_version=version,sealed_secret=EncryptedMFAAdapter().encrypt(secret),expires_at=timezone.now()+timedelta(seconds=120))
    request.session['erp_totp_enrollment']={'id':str(proposal.pk),'binding':binding}
    return proposal,secret


@transaction.atomic
def confirm(request,proposal_id,code):
    user=actor(request)
    proposal=ErpTotpEnrollment.objects.select_for_update().filter(pk=proposal_id,user=user).first()
    now=timezone.now()
    if not proposal or not bound(request,proposal) or proposal.consumed_at:return None
    if proposal.expires_at<=now or proposal.attempts>=5:
        finish(proposal);return None
    proposal.attempts+=1;proposal.save(update_fields=['attempts'])
    version,factors=enrollment_version(user)
    backend=request.session.get(BACKEND_SESSION_KEY)
    if factors or not hmac.compare_digest(version,proposal.factor_version) or not hmac.compare_digest(user.get_session_auth_hash(),proposal.password_version) or backend not in settings.AUTHENTICATION_BACKENDS:
        finish(proposal);return None
    factor=Authenticator(user=user,type='totp',data={'secret':proposal.sealed_secret})
    counter=None
    try:
        secret=totp_secret(factor)
        if isinstance(code,str) and len(code)==app_settings.TOTP_DIGITS and code.isascii() and code.isdecimal():
            current=int(time.time())//app_settings.TOTP_PERIOD
            for value in range(current+app_settings.TOTP_TOLERANCE,current-app_settings.TOTP_TOLERANCE-1,-1):
                if value>=0 and hmac.compare_digest(code,format_hotp_value(hotp_value(secret,value))):counter=value;break
        valid=counter is not None and TOTP(factor).validate_code(code)
    except Exception:valid=False
    if not valid:
        if proposal.attempts>=5:finish(proposal)
        return None
    factor.save(force_insert=True)
    ErpTotpUsage.objects.create(factor=factor,last_counter=counter)
    factor.record_usage();finish(proposal)
    request.session.pop('erp_totp_enrollment',None)
    user.backend=backend
    return user,enrollment_version(user)[0]


@transaction.atomic
def cancel(request,proposal_id):
    user=actor(request)
    proposal=ErpTotpEnrollment.objects.select_for_update().filter(pk=proposal_id,user=user).first()
    if proposal is None or not bound(request,proposal):raise PermissionDenied('No se puede cancelar esta configuración.')
    if proposal.consumed_at is None:finish(proposal)
    # Keep the opaque binding until the next start/logout, so cancellation retries are safe.
    return proposal
