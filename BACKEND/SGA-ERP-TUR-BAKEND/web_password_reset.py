"""Verified-email password recovery. Never removes MFA or establishes a session."""
import hashlib,hmac
from datetime import timedelta
from urllib.parse import urlsplit,urlencode
from django.conf import settings
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password,MinimumLengthValidator,CommonPasswordValidator,NumericPasswordValidator,UserAttributeSimilarityValidator
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode,base36_to_int
from allauth.account.models import EmailAddress
from apps.turismo.models import ErpSecurityEvent
from .web_mfa import enrollment_version

MESSAGE='Si la cuenta tiene un correo verificado habilitado, recibirás instrucciones de recuperación.'


def verified_account(email):
    rows=list(EmailAddress.objects.select_related('user').filter(email__iexact=email,verified=True,user__email__iexact=email,user__is_active=True,user__is_agent=False)[:2])
    return rows[0].user if len(rows)==1 and rows[0].user.has_usable_password() else None


class RecoveryToken(PasswordResetTokenGenerator):
    key_salt='sgacd.erp.verified-email-password-reset.v1'
    def _make_hash_value(self,user,timestamp):
        return super()._make_hash_value(user,timestamp)+enrollment_version(user)[0]
    def check_token(self,user,token):
        if not super().check_token(user,token):return False
        try:age=self._num_seconds(self._now())-base36_to_int(token.split('-')[0])
        except (ValueError,TypeError,AttributeError):return False
        return 0<=age<=900

TOKENS=RecoveryToken()


def configured_url():
    value=getattr(settings,'ERP_PASSWORD_RESET_URL','')
    parsed=urlsplit(value)
    local=getattr(settings,'ERP_PASSWORD_RESET_LOCAL_HTTP',False) and parsed.hostname in {'localhost','127.0.0.1'} and parsed.scheme=='http'
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or (parsed.scheme!='https' and not local):raise ValueError('Trusted reset URL required')
    backend=settings.EMAIL_BACKEND
    if backend.endswith(('console.EmailBackend','filebased.EmailBackend','dummy.EmailBackend')):raise ValueError('Unsafe reset mail backend')
    if not getattr(settings,'ERP_PASSWORD_RESET_MAIL_READY',False):raise ValueError('Verified mail configuration required')
    return value


@sensitive_variables()
def request_reset(email):
    target=configured_url()
    key=hmac.new(settings.SECRET_KEY.encode(),email.casefold().encode(),hashlib.sha256).hexdigest()
    if not cache.add('erp-password-reset:'+key,True,300):return
    user=verified_account(email)
    if user is None:return
    uid=urlsafe_base64_encode(force_bytes(user.pk));token=TOKENS.make_token(user)
    link=target+'#'+urlencode({'reset_uid':uid,'reset_token':token})
    # Neither token nor recipient is returned to HTTP or written to application logs.
    try:send_mail('Recuperación de contraseña ERP','Abre este enlace en un equipo de confianza. Vence en15 minutos.\n'+link+'\nTu segundo factor seguirá siendo obligatorio. Si no solicitaste el cambio, ignora este mensaje.',settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
    except Exception:return  # Same public response; provider monitoring must be configured separately.


@sensitive_variables()
@transaction.atomic
def confirm_reset(uid,token,password):
    try:
        value=urlsafe_base64_decode(uid).decode()
        if not value.isascii() or not value.isdecimal() or not 0<int(value)<2**63:return False
        user=get_user_model().objects.select_for_update().filter(pk=int(value),is_active=True,is_agent=False).first()
    except (ValueError,TypeError,UnicodeError,OverflowError):return False
    if user is None or not TOKENS.check_token(user,token):return False
    verified=verified_account(user.email)
    if verified is None or verified.pk!=user.pk:return False
    if not isinstance(password,str) or not 12<=len(password)<=1024 or check_password(password,user.password):raise DjangoValidationError('La contraseña nueva no cumple la política.')
    validate_password(password,user,[MinimumLengthValidator(12),UserAttributeSimilarityValidator(),CommonPasswordValidator(),NumericPasswordValidator()])
    user.set_password(password);user.save(update_fields=['password'])
    ErpSecurityEvent.objects.create(actor_id=user.pk,kind='password_reset')
    return True


def available():
    if not getattr(settings,'ERP_PASSWORD_RESET_ENABLED',False):return False
    try:configured_url();return True
    except ValueError:return False
