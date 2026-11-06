import os
from django.urls import include, path
from django.http import JsonResponse
from django.db import connection

def health(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return JsonResponse({'status': 'ok', 'service': os.environ['BACKEND_SERVICE']})

urlpatterns = [path('healthz', health)]
if os.environ['BACKEND_SERVICE'] == 'erp-tur':
    urlpatterns += [path('api/v1/mi-negocio/', include('apps.prestadores.mi_negocio.urls'))]
else:
    urlpatterns += [path('', include('puerto_gaitan_turismo.urls'))]
