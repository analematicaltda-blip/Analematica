"""Loopback-only real corporate ASGI + ERP HTTP fixture for browser verification."""
import argparse,json,signal,sys,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--assets',type=Path,required=True);args=parser.parse_args()
sys.path[:0]=[str(ROOT/'BACKEND/SGA-CD-BACKEND/tests'),str(ROOT/'BACKEND/SGA-CD-BACKEND')]
from test_corporate_ledger_integration import DualLedgerIntegration
from fastapi.testclient import TestClient
case=DualLedgerIntegration();case.setUp();recognition=case.prepare_recognition()
html=(ROOT/'FRONTEND/ANALEMATICA-FRONTEND/admin.html').read_text().split('<!-- CORPORATE_LEDGER_PANEL_START -->')[1].split('<!-- CORPORATE_LEDGER_PANEL_END -->')[0]
credentials={'payroll_cost':case.credentials.get('payroll_cost'),'hotel':case.credentials.get('hotel'),'payroll':case.credentials.get('payroll'),'token':case.client.headers['authorization'][7:],'erp_cookie':case.client.cookies.get('sgacd_erp_tur_session'),'recognition':recognition,'opening_existing_journal_id':case.credentials.get('opening_existing_journal_id'),'opening_existing_hash':case.credentials.get('opening_existing_hash')}
if case.credentials.get('native_template'):credentials['native_template']=case.credentials['native_template']
with open(args.assets/'corporate-credentials.json','w',opener=lambda name,flags:__import__('os').open(name,flags,0o600)) as stream:json.dump(credentials,stream)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  if not urlsplit(self.path).path.startswith('/api/v1/workspace/corporate/accounting/commands/'):
   self.send_error(404);return
  length=int(self.headers.get('Content-Length','0'))
  if not 0<length<=8192:self.send_error(413);return
  body=self.rfile.read(length)
  with TestClient(case.client.app) as client:
   response=client.post(self.path,content=body,headers={k:v for k,v in self.headers.items() if k.lower() in {'authorization','cookie','content-type'}})
  self.send_response(response.status_code)
  for key in ['Content-Type','Cache-Control','Vary']:
   if key in response.headers:self.send_header(key,response.headers[key])
  self.end_headers();self.wfile.write(response.content)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path=='/api/v1/workspace/corporate/accounting/report' or path.startswith('/api/v1/workspace/corporate/accounting/sources/'):
   with TestClient(case.client.app) as client:
    response=client.get(self.path,headers={k:v for k,v in self.headers.items() if k.lower() in {'authorization','cookie','accept'}})
   self.send_response(response.status_code)
   for key in ['Content-Type','Cache-Control','Vary']:
    if key in response.headers:self.send_header(key,response.headers[key])
   self.end_headers();self.wfile.write(response.content);return
  if path=='/':
   content=('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><body style="background:#0A1128;color:white;font-family:Arial,sans-serif;margin:8px">'+html+'<script src="/connection.js"></script><script src="/fiscal-envelope-runtime.js"></script><script src="/accounting-fiscal-package.js"></script><script src="/accounting-customer-store.js"></script><script src="/accounting-ubl-draft.js"></script><script src="/accounting-offline.js"></script><script src="/accounting-remediation.js"></script><script src="/accounting-ledger.js"></script><script src="/native-purchases.js"></script><script src="/payroll-costs.js"></script>').encode();mime='text/html; charset=utf-8'
  elif path in {'/connection.js','/accounting-ledger.js','/native-purchases.js','/payroll-costs.js','/accounting-remediation.js','/accounting-offline.js','/accounting-ubl-draft.js','/fiscal-envelope-runtime.js','/accounting-fiscal-package.js','/accounting-customer-store.js'}:content=(ROOT/'FRONTEND/ANALEMATICA-FRONTEND/js'/path[1:]).read_bytes();mime='text/javascript; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(content)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt()))
try:
 print('READY '+str(server.server_port),flush=True);server.serve_forever()
except KeyboardInterrupt:pass
finally:
 server.server_close();case.client.close();case.tearDown();case.doCleanups()
