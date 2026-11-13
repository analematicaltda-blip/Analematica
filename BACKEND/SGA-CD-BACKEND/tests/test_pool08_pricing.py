"""SGA-owned pricing routes, permissions and transactional persistence."""
import runpy,unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_pricing_cases import PricingCases
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')),run_name='pricing_sga_fixture')
from app.commercial.pool08.pricing_models import CommercialPrice,PriceEvent
from app.models.workspace import WorkspaceGrant
class Checks(PricingCases,unittest.TestCase):
 setUp=fixture['CRMChecks'].setUp
 tearDown=fixture['CRMChecks'].tearDown
 login=fixture['CRMChecks'].login
 def data(self,r):return r.json()
 def call(self,method='get',body=None,ref=None,section='list'):
  path='price-commands' if method=='post' else ('price-receipts/'+ref if section=='receipt' else 'prices'+('/'+ref if ref else '')+('/history' if section=='history' else ''))
  return getattr(self.client,method)('/api/v1/commercial-unified/crm/'+path,**({'json':body} if method=='post' else {}))
 def test_other_company_and_revocation(self):
  ref=self.create();self.login('other-admin_empresa');self.assertEqual(self.call(ref=ref).status_code,404);self.assertEqual(self.data(self.call())['items'],[]);self.login('full-jefe_area');self.assertEqual(self.call().status_code,403)
 def test_non_manager_read_and_zero_discount_only(self):
  ref=self.create();self.login('full-jefe_area');grant=self.db.query(WorkspaceGrant).filter_by(user_id=self.users['full-jefe_area'],permission='crm').one();grant.enabled=True;self.db.commit();self.assertEqual(self.call().status_code,200);self.assertEqual(self.call('post',self.body(**self.values())).status_code,403);self.assertEqual(self.call('post',self.offer(ref)).status_code,403);self.assertEqual(self.call('post',self.offer(ref,discount_bps=0)).status_code,200)
 def test_audit_failure_rolls_back_price(self):
  from sqlalchemy import event
  def fail(*args):raise RuntimeError('audit unavailable')
  event.listen(PriceEvent,'before_insert',fail)
  try:
   with self.assertRaises(RuntimeError):self.call('post',self.body(**self.values()))
  finally:event.remove(PriceEvent,'before_insert',fail)
  self.assertEqual(self.db.query(CommercialPrice).count(),0)
 def test_history_tampering_blocks_next_write(self):
  ref=self.create();self.call('post',self.body('update',ref,1,title='Revisión'));row=self.db.query(PriceEvent).filter_by(item_id=ref).order_by(PriceEvent.sequence).first();v=copy.deepcopy(row.document);v['data']['unit_price']='0.01';row.document=v;self.db.commit();self.assertEqual(self.call(ref=ref,section='history').status_code,503);self.assertEqual(self.call('post',self.body('update',ref,2,title='Bypass')).status_code,503)
if __name__=='__main__':unittest.main()
