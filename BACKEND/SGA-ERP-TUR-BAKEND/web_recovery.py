"""Issue/rotate recovery codes only after password and a fresh hardware-independent TOTP proof."""
import hmac,re,time
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import TOTP,hotp_value,format_hotp_value
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from apps.common.mfa_adapter import EncryptedMFAAdapter
from apps.turismo.models import ErpTotpUsage,ErpSecurityEvent
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied
from .web_enrollment import actor
from .web_mfa import enrollment_version,totp_secret


@transaction.atomic
def issue(request,password,code):
    user=actor(request)
    if not isinstance(password,str) or not 1<=len(password)<=1024 or not check_password(password,user.password):
        raise AuthenticationFailed('Contraseña no válida.')
    backend=request.session.get(BACKEND_SESSION_KEY)
    if backend not in settings.AUTHENTICATION_BACKENDS:raise PermissionDenied('Reinicia tu sesión.')
    factors=list(Authenticator.objects.select_for_update().filter(user=user).order_by('pk'))
    totps=[factor for factor in factors if factor.type=='totp']
    backups=[factor for factor in factors if factor.type=='recovery_codes']
    if len(totps)!=1 or len(backups)>1 or any(factor.type not in {'totp','recovery_codes'} for factor in factors):
        raise PermissionDenied('Se requiere un factor TOTP compatible.')
    if app_settings.TOTP_INSECURE_BYPASS_CODE or app_settings.TOTP_DIGITS not in (6,8) or app_settings.TOTP_TOLERANCE not in (0,1) or not 15<=app_settings.TOTP_PERIOD<=60 or not 8<=app_settings.RECOVERY_CODE_DIGITS<=32 or not 1<=app_settings.RECOVERY_CODE_COUNT<=100:
        raise PermissionDenied('La política MFA requiere revisión.')
    factor=totps[0];now=timezone.now()
    usage,_=ErpTotpUsage.objects.select_for_update().get_or_create(factor=factor)
    if usage.locked_until and usage.locked_until>now:return None
    if usage.locked_until:usage.failures=0;usage.locked_until=None
    counter=None
    try:
        secret=totp_secret(factor)
        if isinstance(code,str) and re.fullmatch('[0-9]{'+str(app_settings.TOTP_DIGITS)+'}',code):
            current=int(time.time())//app_settings.TOTP_PERIOD
            for value in range(current+app_settings.TOTP_TOLERANCE,current-app_settings.TOTP_TOLERANCE-1,-1):
                if value>=0 and hmac.compare_digest(code,format_hotp_value(hotp_value(secret,value))):counter=value;break
        valid=counter is not None and counter>usage.last_counter and TOTP(factor).validate_code(code)
    except Exception:valid=False
    if not valid:
        usage.failures+=1
        if usage.failures>=5:usage.locked_until=now+timedelta(minutes=5)
        usage.save();return None  # Commit failures; the view raises after atomic exits.
    usage.last_counter=counter;usage.failures=0;usage.locked_until=None;usage.save()
    data={'seed':EncryptedMFAAdapter().encrypt(RecoveryCodes.generate_seed()),'used_mask':0}
    if backups:
        backup=backups[0];backup.data=data;backup.save(update_fields=['data'])
    else:backup=Authenticator.objects.create(user=user,type='recovery_codes',data=data)
    ErpSecurityEvent.objects.create(actor_id=user.pk,kind='recovery_rotated' if backups else 'recovery_issued',factor_id=backup.pk)
    factor.record_usage();user.backend=backend
    return user,enrollment_version(user)[0],RecoveryCodes(backup).get_unused_codes()
