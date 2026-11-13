"""Owned builder invariants, explicit rollback, input bounds and immutable version behavior."""
import unittest,importlib.util,sys,types,copy,uuid
from pathlib import Path
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[3]
def cases(folder,n):
 name='landing_rules_'+str(n);pkg=types.ModuleType(name);pkg.__path__=[str(ROOT/folder)];sys.modules[name]=pkg
 def load(part):
  spec=importlib.util.spec_from_file_location(name+'.'+part,ROOT/folder/(part+'.py'));m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
 crm=load('crm');load('opportunities');m=load('landings')
 class Store:
  scope='company';provider='provider'
  def __init__(self):self.items={};self.audit=[];self.fail=False
  @contextmanager
  def transaction(self):
   old=copy.deepcopy((self.items,self.audit))
   try:yield
   except Exception:self.items,self.audit=old;raise
  def lock(self):pass
  def get(self,ref):return copy.deepcopy(self.items.get(ref))
  def save(self,item,rev):self.items[item['id']]=copy.deepcopy(item)
  def append(self,event):
   if self.fail:raise RuntimeError('audit unavailable')
   self.audit.append(copy.deepcopy(event))
  def event(self,rid):return next((x for x in self.audit if x['id']==rid),None)
  def last_event(self,ref):return next((x for x in reversed(self.audit) if x['item_id']==ref),None)
  def events(self,ref):return iter(x for x in self.audit if x['item_id']==ref)
  def list(self,*args):return [copy.deepcopy(x) for x in self.items.values()],False
  def find_code(self,code):return any(x['code']==code for x in self.items.values())
 class CRM:
  actor='actor';manager=True
  def authorize(self):return types.SimpleNamespace(principal={'is_manager':self.manager})
 class Checks(unittest.TestCase):
  def setUp(self):self.store=Store();self.crm=CRM();self.b=m.Landings(self.store,self.crm)
  def content(self,title='Página propia'):return dict(brand='Marca',title=title,description='Descripción',template='DEPORTES',blocks=[dict(kind='HERO',heading='Bienvenidos',body='Experiencia',url='',label='')])
  def body(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,landing_id=ref,expected_revision=rev,data=data)
  def create(self):return self.b.command(self.body(slug='pagina-propia',content=self.content()))['landing_id']
  def test_revoke_manager_rejects_even_receipt_replay(self):
   body=self.body(slug='pagina-propia',content=self.content());self.b.command(body);self.crm.manager=False
   for call in [lambda:self.b.command(body),self.b.list,lambda:self.b.receipt(body['request_id'])]:
    with self.assertRaises(crm.CRMError):call()
  def test_audit_failure_rolls_back_snapshot_and_publication(self):
   self.store.fail=True
   with self.assertRaises(RuntimeError):self.create()
   self.assertEqual(self.store.items,{});self.assertEqual(self.store.audit,[])
  def test_version_approval_stale_and_restore_never_autopublishes(self):
   ref=self.create();self.b.command(self.body('approve',ref,1,confirmed=True));self.b.command(self.body('edit',ref,2,content=self.content('Cambió')))
   with self.assertRaises(crm.CRMError):self.b.command(self.body('publish',ref,3,confirmed=True))
   self.b.command(self.body('restore',ref,3,version=1));item=self.b.get(ref);self.assertEqual(item['versions'][-1]['restored_from'],1);self.assertIsNone(item['approved_digest']);self.assertIsNone(item['published_version'])
  def test_history_tamper_blocks_further_mutation(self):
   ref=self.create();self.b.command(self.body('approve',ref,1,confirmed=True));self.store.audit[0]['operation']='forged'
   with self.assertRaises(crm.CRMError):self.b.command(self.body('publish',ref,2,confirmed=True))
  def test_provider_bound_receipt_and_nonce_conflict(self):
   body=self.body(slug='pagina-propia',content=self.content());self.b.command(body);self.store.provider='another-provider'
   with self.assertRaises(crm.CRMError):self.b.command(body)
   with self.assertRaises(crm.CRMError):self.b.receipt(body['request_id'])
  def test_slug_unique_and_version_bounded(self):
   ref=self.create()
   with self.assertRaises(crm.CRMError):self.create()
   for rev in range(1,20):self.b.command(self.body('edit',ref,rev,content=self.content('v'+str(rev))))
   with self.assertRaises(crm.CRMError):self.b.command(self.body('edit',ref,20,content=self.content()))
   self.assertEqual(len(self.b.get(ref)['versions']),20)
  def test_malformed_structures_and_unsafe_links_are_domain_rejections(self):
   for value in [[],{},None]:
    c=self.content();c['template']=value
    with self.assertRaises(crm.CRMError):m.content(c)
   for url in ['javascript:alert(1)','http://example.test','https://user:password@example.test','https://[bad','https://example.test:8888','https://example.test/with space']:
    c=self.content();c['blocks'][0].update(kind='CTA',url=url,label='Abrir')
    with self.assertRaises(crm.CRMError):m.content(c)
  def test_render_escapes_all_user_fields_and_preserves_blue_white(self):
   c=self.content('<img src=x onerror=alert(1)>');c['blocks'][0]['body']='<script>alert(1)</script>';out=m.render(c);self.assertNotIn('<script>',out);self.assertNotIn('<img ',out);self.assertIn('&lt;script&gt;',out);self.assertIn('color:#fff',out);self.assertIn('DEPORTES',c['template'])
  def test_revision_limit_never_prevents_withdrawal(self):
   ref=self.create()
   for rev in range(1,199):self.b.command(self.body('approve',ref,rev,confirmed=True))
   self.b.command(self.body('publish',ref,199,confirmed=True));self.assertEqual(self.b.get(ref)['revision'],200)
   self.b.command(self.body('unpublish',ref,200,confirmed=True));self.assertIsNone(self.b.get(ref)['published_version']);self.assertEqual(self.b.get(ref)['revision'],201)
   with self.assertRaises(crm.CRMError):self.b.command(self.body('approve',ref,201,confirmed=True))
  def test_replay_does_not_add_version_or_event(self):
   body=self.body(slug='pagina-propia',content=self.content());a=self.b.command(body);b=self.b.command(body);self.assertEqual(a['landing_id'],b['landing_id']);self.assertTrue(b['replayed']);self.assertEqual(len(self.store.audit),1);self.assertTrue(self.b.history(a['landing_id'])['history_verified'])
 Checks.__name__='LandingRules'+str(n);return Checks
for i,folder in enumerate(['BACKEND/SGA-CD-BACKEND/app/commercial/pool08','BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08','BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08']):globals()['Rules'+str(i)]=cases(folder,i)
if __name__=='__main__':unittest.main()
