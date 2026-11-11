"""Disposable loopback WSGI harness, native backends only; never deploy."""
import argparse,os,sys,runpy,json,importlib
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--system',choices=['analematica','erp-tur','turismo'],required=True);parser.add_argument('--directory',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[3]
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='army_native_http_fixture')
case=fixture['AdapterTests']();case.setUp()
from django.db import connection
from apps.core_erp.outbox_models import EventAuditLog
if EventAuditLog._meta.db_table not in connection.introspection.table_names():
 with connection.schema_editor() as editor:editor.create_model(EventAuditLog)
from django.conf import settings
from django.urls import clear_url_caches
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
os.environ['BACKEND_SERVICE']=args.system
if args.system=='analematica':
 sys.path.insert(0,str(root/'BACKEND/ANALEMATICA-BACKEND'));settings.ROOT_URLCONF='deployment.army_urls'
else:
 sys.modules.pop('tourism_urls',None);settings.ROOT_URLCONF='tourism_urls'
clear_url_caches();case.post()
credentials={'token':str(AccessToken.for_user(case.user)),'other_token':str(AccessToken.for_user(case.other)),
 'provider_id':str(case.provider.pk),'company_id':str(case.tenant.pk),'day':timezone.localdate().isoformat(),
 'sgacd_modules_loaded':any(name.startswith('app.services') or name.startswith('app.agents') for name in sys.modules)}
with open(args.directory/'native.json','x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(credentials,stream)
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server,WSGIRequestHandler
class Quiet(WSGIRequestHandler):
 def log_message(self,*args):pass
server=make_server('127.0.0.1',0,get_wsgi_application(),handler_class=Quiet)
print('READY '+str(server.server_port),flush=True);server.serve_forever()
