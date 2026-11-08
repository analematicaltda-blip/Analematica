"""Password-bound, session-bound TOTP challenge with persistent replay prevention."""
import base64,hashlib,hmac,json,re,secrets,time,math
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.middleware.csrf import rotate_token
from allauth.mfa.models import Authenticator
from allauth.mfa import app_settings
from allauth.mfa.totp.internal.auth import hotp_value,format_hotp_value,TOTP
from apps.common.mfa_adapter import EncryptedMFAAdapter,PREFIX
from apps.turismo.models import ErpLoginChallenge,ErpTotpUsage,ErpSecurityEvent
from rest_framework.exceptions import PermissionDenied,Throttled


def enrollment_version(user):
    rows=list(Authenticator.objects.filter(user_id=user.pk).order_by('pk').values('id','type','data'))
    value=json.dumps({'factors':rows,'policy':{'digits':app_settings.TOTP_DIGITS,'period':app_settings.TOTP_PERIOD,'tolerance':app_settings.TOTP_TOLERANCE,'bypass':bool(getattr(settings,'MFA_TOTP_INSECURE_BYPASS_CODE',None))}},sort_keys=True,separators=(',',':')).encode()
    return hmac.new(settings.SECRET_KEY.encode(),value,hashlib.sha256).hexdigest(),rows


def totp_secret(factor):
    sealed=factor.data.get('secret')
    if not isinstance(sealed,str) or not sealed.startswith(PREFIX):raise ValueError('Encrypted enrollment required')
    secret=EncryptedMFAAdapter().decrypt(sealed)
    if len(secret)>512 or len(base64.b32decode(secret,casefold=True))<16:raise ValueError('Invalid TOTP enrollment')
    return secret


def session_factor_valid(user,session):
    version,rows=enrollment_version(user)
    stored=session.get('erp_factor_version','')
    if not isinstance(stored,str) or not hmac.compare_digest(stored,version):return False
    if any(row['type'] not in {'totp','recovery_codes'} for row in rows):return False
    if rows and session.get('erp_mfa_verified') is not True:return False
    return True


def begin(request,user):
    version,rows=enrollment_version(user)
    if getattr(settings,'MFA_TOTP_INSECURE_BYPASS_CODE',None):raise PermissionDenied('La configuración de verificación requiere revisión.')
    if any(row['type'] not in {'totp','recovery_codes'} for row in rows):raise PermissionDenied('Este tipo de segundo factor aún requiere su flujo específico.')
    factors=[row for row in rows if row['type']=='totp']
    if len(factors)!=1:raise PermissionDenied('Se requiere un segundo factor compatible y verificado.')
    factor=Authenticator.objects.get(pk=factors[0]['id'])
    usage=ErpTotpUsage.objects.filter(factor=factor).first()
    if usage and usage.locked_until and usage.locked_until>timezone.now():raise Throttled(wait=math.ceil((usage.locked_until-timezone.now()).total_seconds()),detail='Demasiados intentos con el segundo factor.')
    try:totp_secret(factor)
    except Exception:raise PermissionDenied('El registro MFA requiere revisión de su almacenamiento seguro.')
    from django.contrib.auth import logout
    from django.contrib.auth.models import AnonymousUser
    logout(request._request);request.user=AnonymousUser()
    request.session.cycle_key();rotate_token(request._request)
    binding=secrets.token_urlsafe(32)
    challenge=ErpLoginChallenge.objects.create(user=user,factor=factor,backend=user.backend,binding_digest=hashlib.sha256(binding.encode()).hexdigest(),password_version=user.get_session_auth_hash(),factor_version=version,expires_at=timezone.now()+timedelta(seconds=120))
    request.session['erp_pending_mfa']={'id':str(challenge.pk),'binding':binding}
    request.session.set_expiry(120)
    return challenge


def pending(request):
    data=request.session.get('erp_pending_mfa')
    if not isinstance(data,dict):return None
    try:
        challenge=ErpLoginChallenge.objects.select_related('user').filter(pk=data['id'],consumed_at__isnull=True,expires_at__gt=timezone.now(),attempts__lt=5).first()
        if challenge and challenge.factor_id and challenge.user.is_active and hmac.compare_digest(challenge.password_version,challenge.user.get_session_auth_hash()) and hmac.compare_digest(challenge.factor_version,enrollment_version(challenge.user)[0]) and hmac.compare_digest(challenge.binding_digest,hashlib.sha256(data['binding'].encode()).hexdigest()):return challenge
    except (KeyError,ValueError,TypeError,AttributeError,DjangoValidationError):pass
    return None


@transaction.atomic
def verify(request,challenge_id,code,recovery=False):
    # Return failures so the transaction commits attempt counters before the view raises.
    challenge=ErpLoginChallenge.objects.select_for_update().filter(pk=challenge_id).first()
    data=request.session.get('erp_pending_mfa')
    now=timezone.now()
    if not challenge or not isinstance(data,dict):return None
    binding=data.get('binding','')
    if not isinstance(binding,str) or data.get('id')!=str(challenge.pk) or not hmac.compare_digest(challenge.binding_digest,hashlib.sha256(binding.encode()).hexdigest()):return None
    if challenge.consumed_at or challenge.expires_at<=now or challenge.attempts>=5:return None
    challenge.attempts+=1;challenge.save(update_fields=['attempts'])
    from django.contrib.auth import get_user_model
    user=get_user_model().objects.select_for_update().get(pk=challenge.user_id)
    factors=list(Authenticator.objects.select_for_update().filter(user_id=user.pk).order_by('pk'))
    factor=next((item for item in factors if item.pk==challenge.factor_id),None)
    version,rows=enrollment_version(user)
    if not user.is_active or getattr(user,'is_agent',False) or not factor or factor.type!='totp' or any(row['type'] not in {'totp','recovery_codes'} for row in rows) or not hmac.compare_digest(version,challenge.factor_version) or not hmac.compare_digest(user.get_session_auth_hash(),challenge.password_version):return None
    if challenge.backend not in settings.AUTHENTICATION_BACKENDS:return None
    usage,_=ErpTotpUsage.objects.select_for_update().get_or_create(factor=factor)
    if usage.locked_until and usage.locked_until>now:return None
    if usage.locked_until:
        usage.failures=0;usage.locked_until=None
    counter=None
    recovery_valid=False
    if recovery and getattr(settings,'ERP_RECOVERY_CODES_ENABLED',False) and 8<=app_settings.RECOVERY_CODE_DIGITS<=32 and 1<=app_settings.RECOVERY_CODE_COUNT<=100:
        recovery_factors=[item for item in factors if item.type=='recovery_codes']
        if len(recovery_factors)==1:
            backup=recovery_factors[0]
            try:
                # Require the current encrypted-seed format; no legacy plaintext fallback.
                seed=backup.data.get('seed')
                if not isinstance(seed,str) or not seed.startswith(PREFIX) or 'migrated_codes' in backup.data:raise ValueError()
                EncryptedMFAAdapter().decrypt(seed)
                from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
                if isinstance(code,str) and re.fullmatch('[0-9]{'+str(app_settings.RECOVERY_CODE_DIGITS)+'}',code):
                    recovery_valid=RecoveryCodes(backup).validate_code(code)
            except Exception:recovery_valid=False
    try:
        secret=totp_secret(factor)
        if app_settings.TOTP_INSECURE_BYPASS_CODE or app_settings.TOTP_TOLERANCE not in (0,1) or not 15<=app_settings.TOTP_PERIOD<=60 or app_settings.TOTP_DIGITS not in (6,8):raise ValueError('Unsupported TOTP policy')
        if not recovery and isinstance(code,str) and re.fullmatch('[0-9]{'+str(app_settings.TOTP_DIGITS)+'}',code):
            current=int(time.time())//app_settings.TOTP_PERIOD
            for value in range(current+app_settings.TOTP_TOLERANCE,current-app_settings.TOTP_TOLERANCE-1,-1):
                if value>=0 and hmac.compare_digest(code,format_hotp_value(hotp_value(secret,value))):counter=value;break
    except Exception:counter=None
    valid=recovery_valid or (counter is not None and counter>usage.last_counter)
    if valid and not recovery:
        try:valid=TOTP(factor).validate_code(code)
        except Exception:valid=False
    if not valid:
        usage.failures+=1
        if usage.failures>=5:usage.locked_until=now+timedelta(minutes=5)
        usage.save();return None
    if not recovery:usage.last_counter=counter
    usage.failures=0;usage.locked_until=None;usage.save()
    challenge.consumed_at=now;challenge.save(update_fields=['consumed_at'])
    if recovery:ErpSecurityEvent.objects.create(actor_id=user.pk,kind='recovery_used',challenge_id=challenge.pk,factor_id=backup.pk)
    factor.record_usage()
    user.backend=challenge.backend
    return user,enrollment_version(user)[0]


def recovery_available(user):
    if not getattr(settings,'ERP_RECOVERY_CODES_ENABLED',False) or not 8<=app_settings.RECOVERY_CODE_DIGITS<=32 or not 1<=app_settings.RECOVERY_CODE_COUNT<=100:return False
    rows=list(Authenticator.objects.filter(user_id=user.pk,type='recovery_codes'))
    if len(rows)!=1:return False
    factor=rows[0]
    try:
        if not isinstance(factor.data.get('seed'),str) or not factor.data['seed'].startswith(PREFIX) or 'migrated_codes' in factor.data:return False
        from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
        return bool(RecoveryCodes(factor).get_unused_codes())
    except Exception:return False
