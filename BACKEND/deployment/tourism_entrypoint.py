"""Load the real Django application; fail visibly if its model graph is invalid."""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourism_settings'
import django
django.setup()
from django.core.management import call_command
call_command('check')
if os.environ.get('DJANGO_MIGRATE') == '1':
    call_command('migrate', interactive=False)
os.execvp('gunicorn', ['gunicorn', '--bind', '0.0.0.0:8000', '--workers', os.environ.get('WEB_CONCURRENCY', '2'), '--access-logfile', '-', 'puerto_gaitan_turismo.wsgi:application'])
