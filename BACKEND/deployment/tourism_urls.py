import os
from django.urls import include, path
from django.http import JsonResponse
from django.db import connection

def health(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return JsonResponse({'status': 'ok', 'service': os.environ['BACKEND_SERVICE']})

def readiness(request):
    from schema_readiness import inspect_schema
    report = inspect_schema()
    return JsonResponse({**report, 'service': os.environ['BACKEND_SERVICE']}, status=200 if report['status']=='ready' else 503, headers={'Cache-Control':'no-store'})

urlpatterns = [path('healthz', health), path('readyz', readiness)]
if os.environ['BACKEND_SERVICE'] == 'erp-tur':
    urlpatterns += [path('api/v1/finance/wallet/', include('apps.wallet.urls')), path('api/v1/mi-negocio/', include('apps.prestadores.mi_negocio.urls'))]
else:
    urlpatterns += [path('', include('puerto_gaitan_turismo.urls'))]

if os.environ['BACKEND_SERVICE']=='erp-tur':
    from apps.prestadores.mi_negocio.web_session import PasswordResetRequest,PasswordResetConfirm,SessionStatus,SessionLogin,SessionLogout,SessionMfa,SessionRecovery,RecoveryIssue,SessionSecurityEvents,EnrollmentStart,EnrollmentConfirm,EnrollmentCancel
    urlpatterns += [
        path('api/v1/erp-session/password-reset/request/',PasswordResetRequest.as_view()),
        path('api/v1/erp-session/password-reset/confirm/',PasswordResetConfirm.as_view()),
        path('api/v1/erp-session/',SessionStatus.as_view(),name='erp-session-status'),
        path('api/v1/erp-session/login/',SessionLogin.as_view(),name='erp-session-login'),
        path('api/v1/erp-session/logout/',SessionLogout.as_view(),name='erp-session-logout'),
        path('api/v1/erp-session/mfa/',SessionMfa.as_view(),name='erp-session-mfa'),
        path('api/v1/erp-session/security-events/',SessionSecurityEvents.as_view()),path('api/v1/erp-session/recovery/issue/',RecoveryIssue.as_view()),path('api/v1/erp-session/recovery/',SessionRecovery.as_view()),
        path('api/v1/erp-session/enrollment/start/',EnrollmentStart.as_view()),
        path('api/v1/erp-session/enrollment/confirm/',EnrollmentConfirm.as_view()),
        path('api/v1/erp-session/enrollment/cancel/',EnrollmentCancel.as_view()),
    ]
