"""Independent native Analemática army WSGI entry point."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','deployment.army_settings')
from django.core.wsgi import get_wsgi_application
application=get_wsgi_application()
