"""Actual SGA sales bridge over loopback HTTP to native JWT/HMAC ingress.
Shares a disposable native connection with its server thread; not a concurrency
or TLS qualification. Lost HTTP acknowledgment is injected after real posting.
"""
import runpy,unittest,threading,json,os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_saga_check.py')),run_name='sales_saga_http_fixture')
from django.db import connection,connections
from django.core.handlers.wsgi import WSGIRequest
from rest_framework_simplejwt.tokens import AccessToken
from wsgiref.simple_server import make_server,WSGIRequestHandler
from app.commercial.pool08.sales_bridge import Bridge
class HTTPChecks(fixture['SagaChecks']):
 def setUp(self):
  super().setUp();db=connection._connections['default'];db.inc_thread_sharing();self.addCleanup(db.dec_thread_sharing)
  class Quiet(WSGIRequestHandler):
   def log_message(self,*args):pass
  def app(environ,start):
   req=WSGIRequest(environ);action=req.path.rstrip('/').rsplit('/',1)[-1];body=json.loads(req.body);response=self.api.SaleSourceView.as_view()(req,action=action);response.render()
   lost=self.drop and action=='command' and body['body']['command']['operation'] in ('confirm','reverse','cancel') and response.status_code==200
   if lost:self.drop=False;start('503 Service Unavailable',[('Content-Type','application/json')]);return [b'{"code":"SYNTHETIC_LOST_ACK"}']
   start(str(response.status_code)+' '+response.reason_phrase,list(response.items()));return [response.content]
  self.server=make_server('127.0.0.1',0,app,handler_class=Quiet)
  def serve():connections['default']=db;self.server.serve_forever(poll_interval=.05)
  self.thread=threading.Thread(target=serve,daemon=True);self.thread.start()
  def stop():self.server.shutdown();self.thread.join(timeout=3);self.server.server_close()
  self.addCleanup(stop)
  env=patch.dict(os.environ,COMMERCIAL_SALES_LEDGER_ORIGIN='http://127.0.0.1:'+str(self.server.server_port),COMMERCIAL_SALES_LEDGER_SYSTEM='erp-tur',COMMERCIAL_SALES_ALLOW_LOOPBACK_TESTS='1');env.start();self.addCleanup(env.stop)
  request=SimpleNamespace(cookies={},headers={'x-native-ledger-authorization':'Bearer '+str(AccessToken.for_user(self.n.base.user))},url=SimpleNamespace(scheme='http'))
  self.sales.bridge=Bridge(self.crm,request)
if __name__=='__main__':unittest.main()
