"""Server-only settings; original domain modules remain unchanged."""
from tourism_bindings import bind
bind()
from puerto_gaitan_turismo.settings import *
import os
from pathlib import Path

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
FIELD_ENCRYPTION_KEY = os.environ['DJANGO_FIELD_ENCRYPTION_KEY'].encode()
DEBUG = False
# Register both the provider namespace and its relocated ERP child package.
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.insert(INSTALLED_APPS.index('apps.prestadores.mi_negocio.gestion_comercial.apps.GestionComercialConfig'), 'apps.prestadores.mi_negocio.apps.MiNegocioConfig')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = [item for item in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if item]
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SSL_REDIRECT', '0') == '1'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
DATABASE_ROUTERS = []
ROOT_URLCONF = 'tourism_urls'
# Wallet/delivery share this service's isolated database until split migrations are supplied.
DATABASES = {'default': DATABASES['default']}
STATIC_ROOT = Path('/state/static')
MEDIA_ROOT = Path('/state/media')
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = os.environ['REDIS_URL']

# Align the current allauth contract and exclude missing static directories.
ACCOUNT_LOGIN_METHODS={'email'}
ACCOUNT_SIGNUP_FIELDS=['email*','password1*','password2*']
STATICFILES_DIRS=[path for path in STATICFILES_DIRS if Path(path).is_dir()]
# Synthetic deception responses are opt-in and require their migrated storage.
if os.environ.get('DJANGO_DECEPTION_ENABLED','0')!='1':
    MIDDLEWARE=[m for m in MIDDLEWARE if m!='apps.defense_deception.middleware.DeceptionMiddleware']

# Isolated, opt-in browser session and encrypted MFA storage.
ERP_WEB_SESSION_ENABLED=os.environ.get('ERP_WEB_SESSION_ENABLED','0')=='1'
ERP_TOTP_ENROLLMENT_ENABLED=os.environ.get('ERP_TOTP_ENROLLMENT_ENABLED','0')=='1'
SESSION_COOKIE_NAME='sgacd_'+os.environ['BACKEND_SERVICE'].replace('-','_')+'_session'
CSRF_COOKIE_NAME='sgacd_'+os.environ['BACKEND_SERVICE'].replace('-','_')+'_csrf'
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Strict'
CSRF_COOKIE_SAMESITE='Strict'
SESSION_COOKIE_PATH='/api/'
CSRF_COOKIE_PATH='/api/'
MFA_ADAPTER='apps.common.mfa_adapter.EncryptedMFAAdapter'

ERP_RECOVERY_CODES_ENABLED=os.environ.get('ERP_RECOVERY_CODES_ENABLED','0')=='1'

ERP_RECOVERY_ISSUANCE_ENABLED=os.environ.get('ERP_RECOVERY_ISSUANCE_ENABLED','0')=='1'

ERP_CAPACITY_HOLDS_ENABLED=os.environ.get('ERP_CAPACITY_HOLDS_ENABLED','0')=='1'

ERP_PASSWORD_RESET_ENABLED=os.environ.get('ERP_PASSWORD_RESET_ENABLED','0')=='1'
ERP_PASSWORD_RESET_URL=os.environ.get('ERP_PASSWORD_RESET_URL','')
ERP_PASSWORD_RESET_MAIL_READY=os.environ.get('ERP_PASSWORD_RESET_MAIL_READY','0')=='1'
