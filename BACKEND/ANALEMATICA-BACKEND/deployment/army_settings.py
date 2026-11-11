"""Standalone native accounting army; no SGA-CD API, models or credentials.
Uses the existing monorepo ledger/identity models in this process's own database.
"""
import os,sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
root=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(root/'deployment'),str(root/'SGA-TUR-BAKEND')]
os.environ.setdefault('BACKEND_SERVICE','analematica')
if os.environ['BACKEND_SERVICE']!='analematica':raise ImproperlyConfigured('Native Analemática process required.')
from tourism_settings import *
ROOT_URLCONF='deployment.army_urls'
SESSION_COOKIE_NAME='analematica_army_session'
CSRF_COOKIE_NAME='analematica_army_csrf'
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
