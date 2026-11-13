"""Run generated preview Nginx against actual disposable ERP API; never deploys."""
import argparse,runpy,unittest,uuid,os,tempfile,importlib.util,subprocess,threading,socket,ssl,io,time,re
from pathlib import Path
from unittest.mock import patch
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from PIL import Image
import httpx
from pool08_pricing_cases import PricingCases
from pool08_quotation_cases import QuotationCases
parser=argparse.ArgumentParser();parser.add_argument('--nginx',required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('actual_quote_delivery',ROOT/'FRONTEND/deployment/prepare.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_quotations_http_check.py')),run_name='nginx_quote_fixture');base=fixture['QuotationHTTP']
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
class NginxChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls._class_cleanups=[];base.setUpClass.__func__(cls);cls.addClassCleanup(lambda:base.tearDownClass.__func__(cls));cls.tmp=tempfile.TemporaryDirectory(prefix='quote-nginx-');cls.addClassCleanup(cls.tmp.cleanup);root=Path(cls.tmp.name);cls.root=root
  private=root/'private';private.mkdir(mode=0o700);runtime=root/'runtime';runtime.mkdir();cls.patches=[patch.object(preview,'PRIVATE',private),patch.object(preview,'RUNTIME',runtime),patch.dict(os.environ,{'SGACD_ENABLE_ERP_API':'1'})]
  for p in cls.patches:p.start();cls.addClassCleanup(p.stop)
  preview.certificate();preview.credentials();preview.public_assets();preview.nginx()
  handler=partial(QuietHandler,directory=str(ROOT/'FRONTEND/SGA-ERP-TUR-FRONTEND/public'));cls.static=ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=cls.static.serve_forever,daemon=True).start();cls.addClassCleanup(cls.static.shutdown);cls.addClassCleanup(cls.static.server_close)
  ports=[]
  for _ in range(4):
   s=socket.socket();s.bind(('127.0.0.1',0));ports.append(s.getsockname()[1]);s.close()
  config=(runtime/'nginx.conf').read_text().replace('/etc/nginx/mime.types',str(Path(args.nginx).resolve().parents[1]/'conf/mime.types')).replace('/private/',str(private)+'/').replace('/sites/',str(runtime/'sites')+'/').replace('pid /tmp/nginx.pid;','pid '+str(root/'nginx.pid')+';').replace('/tmp/proxy',str(root/'proxy')).replace('/tmp/body',str(root/'body'))
  # Only container addresses/listeners are localized; all route/auth/CSP directives stay generated.
  for i,port in enumerate(ports):config=config.replace('listen '+str(8440+i)+' ssl;','listen 127.0.0.1:'+str(port)+' ssl;')
  for system in ('erp-tur','analematica'):
   client,cred=cls.servers[system];config=config.replace(system+':8000',str(client.base_url).split('://',1)[1].rstrip('/'))
  config=config.replace('sgacd:8000',str(cls.extra['sga-cd'][0].base_url).split('://',1)[1].rstrip('/')).replace('http://erp-web:3000','http://127.0.0.1:'+str(cls.static.server_port)).replace('http://turismo-web:3000','http://127.0.0.1:'+str(cls.static.server_port))
  cls.config=root/'nginx.conf';cls.config.write_text(config);check=subprocess.run([args.nginx,'-t','-c',str(cls.config)],capture_output=True,text=True,timeout=15);assert check.returncode==0,'Generated Nginx syntax failed: '+check.stderr
  cls.log=open(root/'nginx.log','w');cls.process=subprocess.Popen([args.nginx,'-c',str(cls.config),'-g','daemon off;'],stdout=cls.log,stderr=cls.log);cls.addClassCleanup(cls.log.close)
  def stop():
   cls.process.terminate()
   try:cls.process.wait(timeout=10)
   except subprocess.TimeoutExpired:cls.process.kill();cls.process.wait()
  cls.addClassCleanup(stop);context=ssl.create_default_context(cafile=str(private/'localhost.crt'));cls.client=httpx.Client(base_url='https://localhost:'+str(ports[2]),verify=context,trust_env=False,timeout=15);cls.addClassCleanup(cls.client.close)
  for _ in range(50):
   try:
    cls.client.get('/commercial-quote.html');break
   except httpx.ConnectError:time.sleep(.05)
  else:raise RuntimeError('Local Nginx did not become ready')
 @classmethod
 def tearDownClass(cls):pass
 def unwrap(self,response):
  self.assertEqual(response.status_code,200,response.text[:200]);data=response.json();return data['data'] if data.get('success') is True else data
 body=PricingCases.body
 def test_public_shell_does_not_unlock_private_panels(self):
  for path in ('/commercial-quote.html','/js/commercial-quote-recipient.js','/css/commercial-crm.css'):
   r=self.client.get(path);self.assertEqual(r.status_code,200);self.assertIn("media-src 'self' blob:",r.headers['content-security-policy'])
  self.assertEqual(self.client.get('/commercial-crm.html').status_code,401);self.assertEqual(self.client.get('/api/v1/finance/accounts/').status_code,503)
 def test_actual_tls_proxy_public_acceptance_and_media(self):
  native,cred=self.servers['erp-tur'];prefix='/api/v1/mi-negocio/comercial/unified/';query={'provider_id':cred['provider_id']}
  def post(path,body):return self.unwrap(native.post(prefix+'crm/'+path+'/',params=query,json=body))
  price=post('price-commands',PricingCases.body(self,**PricingCases.values(self)))['item_id'];contact=post('commands',dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Contacto Nginx',origin='SYNTHETIC',responsible_ref=cred['actor_ref'])))['contact_id'];self.contact=contact
  post('quotation-commands',QuotationCases.body(self,'review_capacity',item_id=price,price_revision=1,mode='NOT_APPLICABLE',resource_ref=None,reason='Laboratorio',support_digest='a'*64));image=io.BytesIO();Image.new('RGB',(64,32),(10,30,80)).save(image,format='PNG');asset=str(uuid.uuid4());self.unwrap(native.post(prefix+'crm/quotation-media/'+asset+'/',params=query,content=image.getvalue(),headers={'Content-Type':'image/png'}));ref=post('quotation-commands',QuotationCases.body(self,**QuotationCases.values(self,price,media_ids=[asset])))['quotation_id'];post('quotation-commands',QuotationCases.body(self,'issue',ref,1));link=post('quotation-commands',QuotationCases.body(self,'link',ref,2,confirm_share=True))
  path=prefix+'quote-links/'+ref+'/'+link['link_id']+'/';headers={'X-Quote-Token':link['link_token']};view=self.unwrap(self.client.get(path,headers=headers));self.assertEqual(view['content']['estimate']['total'],'14691.35');r=self.client.get(path+'media/'+asset+'/',headers=headers);self.assertEqual(r.status_code,200);self.assertEqual(r.headers['content-type'],'image/png');self.assertEqual(r.headers['cache-control'],'no-store')
  command=dict(request_id=str(uuid.uuid4()),version=view['version'],content_digest=view['content_digest'],confirmed=True);self.assertEqual(self.unwrap(self.client.post(path,headers=headers,json=command))['status'],'ACCEPTED');self.assertTrue(self.unwrap(self.client.post(path,headers=headers,json=command))['replayed']);self.assertEqual(self.client.get(path,headers={'X-Quote-Token':'0'*64}).status_code,403)
 def test_route_body_limits_remain_specific_and_auth_is_not_bypassed(self):
  prefix='/api/v1/mi-negocio/comercial/unified/crm/'
  r=self.client.post(prefix+'quotation-commands/',content=b'x'*17000,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,413)
  # A media body >16 KiB reaches native authentication; it no longer fails at old 16 KiB gate.
  path=prefix+'quotation-media/'+str(uuid.uuid4())+'/'
  self.assertIn(self.client.post(path,content=b'x'*20000,headers={'Content-Type':'image/png'}).status_code,(401,403))
  self.assertEqual(self.client.post(path,content=b'x'*262145,headers={'Content-Type':'image/png'}).status_code,413)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NginxChecks)).wasSuccessful())
