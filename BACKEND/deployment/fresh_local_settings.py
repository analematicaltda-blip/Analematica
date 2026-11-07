"""Opt-in clean SQLite installation; never reuse a historical database."""
import json
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

directory=Path(os.environ['SGACD_FRESH_LOCAL_DIR']).resolve()
marker=directory/'fresh-local.json'
metadata=json.loads(marker.read_text())
if metadata!={'schema':'fresh-local-v1','service':os.environ['BACKEND_SERVICE']}:
    raise ImproperlyConfigured('The fresh-local marker does not match this service.')

from tourism_settings import *

DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':str(directory/'application.sqlite3'),'OPTIONS':{'timeout':20}}}
import fresh_migrations
MIGRATION_MODULES={path.name:'fresh_migrations.'+path.name for path in Path(fresh_migrations.__file__).parent.iterdir() if path.is_dir() and (path/'__init__.py').exists()}
STATIC_ROOT=directory/'static'
MEDIA_ROOT=directory/'media'
# No automatic task execution or external email in this local-only profile.
EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache','LOCATION':'fresh-local'}}
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
WALLET_INTERNAL_TRANSFERS_ENABLED=os.environ.get('WALLET_INTERNAL_TRANSFERS_ENABLED','0')=='1'
WALLET_DEVICE_APPROVALS_REQUIRED=os.environ.get('WALLET_DEVICE_APPROVALS_REQUIRED','1')!='0'
WALLET_DEVICE_ENROLLMENT_ENABLED=os.environ.get('WALLET_DEVICE_ENROLLMENT_ENABLED','0')=='1'
WALLET_APPROVAL_AUDIENCE=os.environ.get('WALLET_APPROVAL_AUDIENCE','')
