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
    urlpatterns += [path('api/v1/mi-negocio/', include('apps.prestadores.mi_negocio.urls'))]
else:
    urlpatterns += [path('', include('puerto_gaitan_turismo.urls'))]
