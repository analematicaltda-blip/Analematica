"""Opt-in ERP browser session. No JWTs in JavaScript; login explicitly enforces CSRF."""
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters,sensitive_variables
from django.contrib.auth import authenticate,login,logout
from django.middleware.csrf import get_token
from django.utils import timezone
from uuid import UUID
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import APIException,AuthenticationFailed,PermissionDenied,ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

class SessionUnavailable(APIException):
    status_code=503
    default_detail='La sesión web ERP no está habilitada en este entorno.'
    default_code='erp_session_disabled'

class LoginThrottle(AnonRateThrottle):
    scope='erp_session_login'
    rate='5/min'
    def get_ident(self,request):
        # Never let a client-controlled Forwarded/X-Forwarded-For reset the quota.
        return request.META.get('REMOTE_ADDR','unknown')

class ErpSessionAuthentication(SessionAuthentication):
    def authenticate(self,request):
        if not getattr(settings,'ERP_WEB_SESSION_ENABLED',False):return None
        result=super().authenticate(request)
        if result and request.session.get('erp_web_session') is True:
            if getattr(result[0],'is_agent',False):return None
            from .web_mfa import session_factor_valid
            if not session_factor_valid(result[0],request.session):return None
            return result
        return None

class SessionView(APIView):
    authentication_classes=[ErpSessionAuthentication]
    permission_classes=[AllowAny]
    def initial(self,request,*args,**kwargs):
        if not getattr(settings,'ERP_WEB_SESSION_ENABLED',False):raise SessionUnavailable()
        return super().initial(request,*args,**kwargs)
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs)
        response['Cache-Control']='no-store'
        response['Vary']='Cookie'
        return response


def state(request):
    user=request.user
    authenticated=bool(user.is_authenticated and user.is_active and request.session.get('erp_web_session') is True)
    from .web_mfa import pending,recovery_available
    from allauth.mfa import app_settings
    challenge=pending(request) if not authenticated else None
    from .web_mfa import enrollment_version
    factors=enrollment_version(user)[1] if authenticated else []
    enrollment_allowed=authenticated and not factors and getattr(settings,'ERP_TOTP_ENROLLMENT_ENABLED',False)
    from .web_password_reset import available as reset_available
    return {'password_reset_available':reset_available(),'authenticated':authenticated,'user':{'id':user.pk,'username':user.get_username()} if authenticated else None,'csrf_token':get_token(request._request),'totp_enrollment_allowed':bool(enrollment_allowed),'mfa_enabled':bool(factors),'recovery_issuance_allowed':bool(authenticated and request.session.get('erp_mfa_verified') is True and getattr(settings,'ERP_RECOVERY_CODES_ENABLED',False) and getattr(settings,'ERP_RECOVERY_ISSUANCE_ENABLED',False)),'recovery_available':bool(challenge and recovery_available(challenge.user)),'mfa_required':challenge is not None,'challenge_id':str(challenge.pk) if challenge else None,'recovery_digits':app_settings.RECOVERY_CODE_DIGITS,'mfa_digits':app_settings.TOTP_DIGITS}

class SessionStatus(SessionView):
    def get(self,request):return Response(state(request))

class SessionLogin(SessionView):
    authentication_classes=[]
    throttle_classes=[LoginThrottle]
    def post(self,request):
        SessionAuthentication().enforce_csrf(request)
        if not isinstance(request.data,dict) or set(request.data)!={'username','password'}:raise ValidationError('Se requiere usuario y contraseña.')
        username=request.data['username'];password=request.data['password']
        if not isinstance(username,str) or not isinstance(password,str) or not 1<=len(username)<=150 or not 1<=len(password)<=1024:raise AuthenticationFailed('Credenciales no válidas.')
        user=authenticate(request=request._request,username=username,password=password)
        if user is None or not user.is_active or getattr(user,'is_agent',False):raise AuthenticationFailed('Credenciales no válidas.')
        from .web_mfa import enrollment_version,begin
        version,factors=enrollment_version(user)
        if factors:
            begin(request,user)
            return Response(state(request),status=202)
        establish(request,user,version,False)
        return Response(state(request))

def establish(request,user,version,mfa_verified):
    login(request._request,user,backend=user.backend)
    request.session.pop('erp_pending_mfa',None)
    request.session['erp_web_session']=True
    request.session['erp_factor_version']=version
    request.session['erp_mfa_verified']=mfa_verified
    request.session.set_expiry(900)
    request.user=user

class MfaThrottle(LoginThrottle):
    scope='erp_session_mfa'
    rate='10/min'

class SessionMfa(SessionView):
    recovery=False
    authentication_classes=[]
    throttle_classes=[MfaThrottle]
    def post(self,request):
        SessionAuthentication().enforce_csrf(request)
        if not isinstance(request.data,dict) or set(request.data)!={'challenge_id','code'}:raise ValidationError('Se requiere el desafío y el código de verificación.')
        try:challenge_id=UUID(str(request.data['challenge_id']))
        except (ValueError,TypeError):raise ValidationError('Desafío inválido.')
        code=request.data['code']
        if not isinstance(code,str) or len(code)>(64 if self.recovery else 8):raise ValidationError('Código inválido.')
        from .web_mfa import verify
        result=verify(request,challenge_id,code,recovery=True) if self.recovery else verify(request,challenge_id,code)
        if result is None:raise AuthenticationFailed('Código no válido, ya utilizado o desafío vencido. Reinicia el acceso si es necesario.')
        user,version=result
        establish(request,user,version,True)
        return Response(state(request))

class SessionRecovery(SessionMfa):
    recovery=True
    def initial(self,request,*args,**kwargs):
        if not getattr(settings,'ERP_RECOVERY_CODES_ENABLED',False):raise SessionUnavailable()
        return super().initial(request,*args,**kwargs)

class SessionLogout(SessionView):
    def post(self,request):
        SessionAuthentication().enforce_csrf(request)
        logout(request._request)
        request.user=request._request.user
        return Response(state(request))

class EnrollmentThrottle(LoginThrottle):
    scope='erp_totp_enrollment'
    rate='10/min'
    def get_cache_key(self,request,view):
        return self.cache_format % {'scope':self.scope,'ident':self.get_ident(request)+':'+str(request.user.pk)}

class EnrollmentView(SessionView):
    permission_classes=[IsAuthenticated]
    throttle_classes=[EnrollmentThrottle]
    def initial(self,request,*args,**kwargs):
        super().initial(request,*args,**kwargs)
        if not getattr(settings,'ERP_TOTP_ENROLLMENT_ENABLED',False):raise SessionUnavailable()

class EnrollmentStart(EnrollmentView):
    def post(self,request):
        if not isinstance(request.data,dict) or set(request.data)!={'password'}:raise ValidationError('Se requiere confirmar la contraseña.')
        from .web_enrollment import start
        from allauth.mfa import app_settings
        proposal,secret=start(request,request.data['password'])
        return Response({'id':str(proposal.pk),'secret':secret,'digits':app_settings.TOTP_DIGITS,'expires_at':proposal.expires_at,'issuer':'Analematica ERP'},status=201)

class EnrollmentConfirm(EnrollmentView):
    def post(self,request):
        if not isinstance(request.data,dict) or set(request.data)!={'id','code'}:raise ValidationError('Se requiere configuración y código.')
        try:identifier=UUID(str(request.data['id']))
        except (TypeError,ValueError):raise ValidationError('Configuración inválida.')
        code=request.data['code']
        if not isinstance(code,str) or len(code)>8:raise ValidationError('Código inválido.')
        from .web_enrollment import confirm
        result=confirm(request,identifier,code)
        if result is None:raise AuthenticationFailed('Código no válido o configuración vencida. Cancela y reinicia si es necesario.')
        user,version=result
        request.session.cycle_key()
        establish(request,user,version,True)
        return Response(state(request))

class EnrollmentCancel(EnrollmentView):
    def post(self,request):
        if not isinstance(request.data,dict) or set(request.data)!={'id'}:raise ValidationError('Se requiere la configuración.')
        try:identifier=UUID(str(request.data['id']))
        except (TypeError,ValueError):raise ValidationError('Configuración inválida.')
        from .web_enrollment import cancel
        cancel(request,identifier)
        return Response({'cancelled':True})

class RecoveryIssue(SessionView):
    permission_classes=[IsAuthenticated]
    throttle_classes=[EnrollmentThrottle]
    def initial(self,request,*args,**kwargs):
        super().initial(request,*args,**kwargs)
        if not getattr(settings,'ERP_RECOVERY_CODES_ENABLED',False) or not getattr(settings,'ERP_RECOVERY_ISSUANCE_ENABLED',False):raise SessionUnavailable()
    def post(self,request):
        if request.session.get('erp_mfa_verified') is not True:raise PermissionDenied('Se requiere una sesión MFA.')
        if not isinstance(request.data,dict) or set(request.data)!={'password','code'}:raise ValidationError('Se requiere contraseña y código TOTP nuevo.')
        from .web_recovery import issue
        result=issue(request,request.data['password'],request.data['code'])
        if result is None:raise AuthenticationFailed('Código no válido, ya utilizado o factor bloqueado.')
        user,version,codes=result
        request.session.cycle_key();establish(request,user,version,True)
        return Response({'session':state(request),'codes':codes},status=201)

class SessionSecurityEvents(SessionView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        from apps.turismo.models import ErpSecurityEvent
        events=ErpSecurityEvent.objects.filter(actor_id=request.user.pk).order_by('-occurred_at','-id')[:20]
        return Response({'events':[{'id':str(event.pk),'kind':event.kind,'occurred_at':event.occurred_at} for event in events]})

class PasswordResetThrottle(LoginThrottle):
    scope='erp_password_reset'
    rate='5/min'

@method_decorator(sensitive_post_parameters('email','uid','token','password'),name='dispatch')
class PasswordResetView(SessionView):
    authentication_classes=[]
    throttle_classes=[PasswordResetThrottle]
    def initial(self,request,*args,**kwargs):
        super().initial(request,*args,**kwargs)
        if not getattr(settings,'ERP_PASSWORD_RESET_ENABLED',False):raise SessionUnavailable()
        from .web_password_reset import configured_url
        try:configured_url()
        except ValueError:raise SessionUnavailable()

class PasswordResetRequest(PasswordResetView):
    @sensitive_variables()
    def post(self,request):
        SessionAuthentication().enforce_csrf(request)
        if not isinstance(request.data,dict) or set(request.data)!={'email'}:raise ValidationError({'detail':'Se requiere correo electrónico.'})
        from rest_framework.serializers import EmailField
        try:email=EmailField(max_length=254).run_validation(request.data['email'])
        except ValidationError:raise ValidationError({'email':'Correo electrónico inválido.'})
        from .web_password_reset import request_reset,MESSAGE
        request_reset(email)
        return Response({'message':MESSAGE},status=202)

class PasswordResetConfirm(PasswordResetView):
    @sensitive_variables()
    def post(self,request):
        SessionAuthentication().enforce_csrf(request)
        if not isinstance(request.data,dict) or set(request.data)!={'uid','token','password'}:raise ValidationError({'detail':'Se requiere enlace y contraseña nueva.'})
        uid,token=request.data['uid'],request.data['token']
        if not isinstance(uid,str) or not 1<=len(uid)<=64 or not isinstance(token,str) or not 1<=len(token)<=128:raise ValidationError({'detail':'Enlace inválido o vencido.'})
        from .web_password_reset import confirm_reset
        from django.core.exceptions import ValidationError as PasswordError
        try:accepted=confirm_reset(uid,token,request.data['password'])
        except PasswordError:raise ValidationError({'detail':'La contraseña nueva debe ser larga, no común y diferente de los datos personales.'})
        if not accepted:raise ValidationError({'detail':'Enlace inválido o vencido.'})
        return Response({'password_changed':True,'automatic_login':False,'mfa_preserved':True})
