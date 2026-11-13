import runpy,unittest,sys,os,uuid,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_quotation_cases import QuotationCases
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')),run_name='quotation_sga_fixture')
from app.commercial.pool08.quotation_models import CommercialQuotation,QuotationEvent
from unittest.mock import patch
class Checks(QuotationCases,unittest.TestCase):
 domain_path="app.commercial.pool08"
 tearDown=fixture['CRMChecks'].tearDown
 login=fixture['CRMChecks'].login
 def setUp(self):
  fixture['CRMChecks'].setUp(self);env=patch.dict(os.environ,{'COMMERCIAL_QUOTE_LINK_KEY':'synthetic-quotation-test-key-32-chars-only'});env.start();self.addCleanup(env.stop);self.contact=fixture['CRMChecks'].create(self)
 def data(self,r):return r.json()
 def price_call(self,body):return self.client.post('/api/v1/commercial-unified/crm/price-commands',json=body)
 def call(self,method='get',body=None,ref=None,section='list'):
  path='quotation-commands' if method=='post' else 'quotations'+('/'+ref if ref else '')+('/history' if section=='history' else '')
  return getattr(self.client,method)('/api/v1/commercial-unified/crm/'+path,**({'json':body} if method=='post' else {}))
 def upload(self,ref,raw,mime):return self.client.post('/api/v1/commercial-unified/crm/quotation-media/'+ref,content=raw,headers={'Content-Type':mime})
 def public(self,ref,link,body=None,asset=None):
  path='/api/v1/commercial-unified/quote-links/'+ref+'/'+link['link_id']+('/media/'+asset if asset else '');return getattr(self.client,'post' if body else 'get')(path,headers={'X-Quote-Token':link['link_token'],'Authorization':''},**({'json':body} if body else {}))
 def test_other_company_denied_and_owner_revoked_link_blocked(self):
  ref=self.create();self.issue(ref);link=self.link(ref);self.login('other-admin_empresa');self.assertEqual(self.call(ref=ref).status_code,404)
 def test_audit_failure_rolls_back_quote(self):
  from sqlalchemy import event
  price=self.price();self.policy(price)
  def fail(*args):raise RuntimeError('audit unavailable')
  event.listen(QuotationEvent,'before_insert',fail)
  try:
   with self.assertRaises(RuntimeError):self.call('post',self.body(**self.values(price)))
  finally:event.remove(QuotationEvent,'before_insert',fail)
  self.assertEqual(self.db.query(CommercialQuotation).filter(CommercialQuotation.status!='CAPACITY_POLICY').count(),0)
 def test_sga_capacity_source_rechecked_without_booking(self):
  from datetime import datetime,timezone,timedelta
  from app.models.academic import Escenario,EscenarioParte,Reserva
  from app.models.user import Usuario
  user=self.db.get(Usuario,self.users['full-admin_empresa']);space=Escenario(inquilino_id=user.inquilino_id,nombre='Espacio de prueba');self.db.add(space);self.db.flush();part=EscenarioParte(inquilino_id=user.inquilino_id,escenario_id=space.id,nombre_parte='Parte propia',capacidad=2);self.db.add(part);self.db.commit()
  price=self.price();self.policy(price,'REQUIRED',str(part.id));start=datetime.now(timezone.utc)+timedelta(days=1);end=start+timedelta(hours=1);ref=self.create(price,policy=False,service_windows=[dict(item_id=price,start_at=start.isoformat(),end_at=end.isoformat())]);self.issue(ref);link=self.link(ref);self.assertEqual(self.db.query(Reserva).count(),0)
  self.db.add(Reserva(inquilino_id=user.inquilino_id,escenario_parte_id=part.id,usuario_id_reserva=user.id,fecha_inicio=start,fecha_fin=end,estado='Confirmada'));self.db.commit();self.assertEqual(self.public(ref,link,self.acceptance(ref)).status_code,409)
 def test_history_tamper_blocks_issue(self):
  ref=self.create();row=self.db.query(QuotationEvent).filter_by(item_id=ref).first();value=copy.deepcopy(row.document);value['snapshot']['content']['title']='Alterada';row.document=value;self.db.commit();self.assertEqual(self.call('post',self.body('issue',ref,1)).status_code,503)
 # Helpers required by the reused CRM fixture.
 cmd=fixture['CRMChecks'].cmd
 post=fixture['CRMChecks'].post
 get=fixture['CRMChecks'].get
if __name__=='__main__':unittest.main()
