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
