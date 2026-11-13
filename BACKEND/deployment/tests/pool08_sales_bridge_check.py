"""Fixed peer, bounded transport and signed acknowledgment fail-closed contracts."""
import unittest,os,sys,json,copy
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.commercial.pool08.sales_bridge import Bridge
from app.commercial.pool08.source_protocol import wrap
from app.commercial.pool08.crm import CRMError
class BridgeChecks(unittest.TestCase):
 def setUp(self):
  self.env=patch.dict(os.environ,COMMERCIAL_SALES_LEDGER_ORIGIN='https://ledger.example.test',COMMERCIAL_SALES_LEDGER_SYSTEM='erp-tur',COMMERCIAL_SALES_ALLOW_LOOPBACK_TESTS='0',COMMERCIAL_SALES_SOURCE_KEY='synthetic-source-bridge-key-more-than-32');self.env.start();self.addCleanup(self.env.stop)
  crm=SimpleNamespace(actor='7',store=SimpleNamespace(scope='tenant:4'),authorize=lambda:SimpleNamespace(principal={'is_manager':True},session=lambda:{'local_role_fingerprint':'a'*64}))
  self.bridge=Bridge(crm,SimpleNamespace(cookies={},headers={'authorization':'Bearer sga-source-only'},url=SimpleNamespace(scheme='https')))
 def client(self,handler):return httpx.Client(base_url='https://ledger.example.test',transport=httpx.MockTransport(handler)), '/api/v1/mi-negocio/comercial/unified/', ('sgacd_erp_tur_session','sgacd_erp_tur_csrf'),True
 def test_unsigned_or_wrong_context_acknowledgment_is_not_success(self):
  for mode in ['signature','actor']:
   def handler(req):
    context=json.loads(req.content)['context'];response=wrap(context,{'scopes':[]})
    if mode=='signature':response['signature']='0'*64
    else:response=wrap({**context,'actor':'8'},{'scopes':[]})
    return httpx.Response(200,json=response)
   with patch.object(self.bridge,'client',side_effect=lambda:self.client(handler)):
    with self.assertRaises(CRMError) as exc:self.bridge.rpc('scopes',{})
    self.assertEqual(exc.exception.status,503)
 def test_signed_acknowledgment_and_exact_fixed_route(self):
  def handler(req):
   self.assertEqual(req.url.host,'ledger.example.test');self.assertEqual(req.url.path,'/api/v1/mi-negocio/comercial/unified/sale-source/scopes/');self.assertNotIn('sga-source-only',str(req.headers));context=json.loads(req.content)['context'];return httpx.Response(200,json=wrap(context,{'scopes':[]}))
  with patch.object(self.bridge,'client',side_effect=lambda:self.client(handler)):self.assertEqual(self.bridge.rpc('scopes',{}),{'scopes':[]})
 def test_redirect_timeout_response_limit_and_invalid_json_are_uncertain(self):
  for mode in ['redirect','timeout','large','json']:
   def handler(req):
    if mode=='timeout':raise httpx.ReadTimeout('synthetic',request=req)
    return httpx.Response(302,headers={'Location':'https://attacker.invalid'}) if mode=='redirect' else httpx.Response(200,content=b'x'*524289 if mode=='large' else b'not-json')
   with patch.object(self.bridge,'client',side_effect=lambda:self.client(handler)):
    with self.assertRaises(CRMError) as exc:self.bridge.rpc('scopes',{})
    self.assertEqual(exc.exception.status,503)
 def test_missing_or_caller_style_origins_never_select_a_peer(self):
  for origin in ['', 'http://127.0.0.1:99','https://user:password@ledger.example.test','https://ledger.example.test/path','https://ledger.example.test?url=x']:
   with patch.dict(os.environ,COMMERCIAL_SALES_LEDGER_ORIGIN=origin):
    with self.assertRaises(CRMError):self.bridge.settings()
 def test_loopback_exception_is_explicit_and_literal_only(self):
  for host,ok in [('127.0.0.1',True),('localhost',False),('169.254.169.254',False),('192.168.1.2',False)]:
   with patch.dict(os.environ,COMMERCIAL_SALES_ALLOW_LOOPBACK_TESTS='1',COMMERCIAL_SALES_LEDGER_ORIGIN='http://'+host+':99'):
    if ok:self.assertEqual(self.bridge.settings()[0],'http://127.0.0.1:99')
    else:
     with self.assertRaises(CRMError):self.bridge.settings()
if __name__=='__main__':unittest.main()
