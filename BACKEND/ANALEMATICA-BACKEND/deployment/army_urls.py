"""Native Analemática route boundary; never proxies another backend."""
from django.urls import path,include
from django.http import JsonResponse
from django.db import connection

def health(request):
    with connection.cursor() as cursor:cursor.execute('SELECT 1')
    return JsonResponse({'status':'ok','service':'analematica-army'},headers={'Cache-Control':'no-store'})
def readiness(request):
    from schema_readiness import inspect_schema
    report=inspect_schema()
    return JsonResponse({**report,'service':'analematica-army'},status=200 if report['status']=='ready' else 503,headers={'Cache-Control':'no-store'})
urlpatterns=[path('healthz',health),path('readyz',readiness),
 path('api/v1/accounting-army/',include('apps.admin_plataforma.gestion_contable.contabilidad.agent_army.urls'))]
