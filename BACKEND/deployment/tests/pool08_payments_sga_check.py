"""SGA-owned payment intentions after an actual native ledger sale; synthetic links only."""
import runpy,unittest
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_saga_check.py')),run_name='payment_sga_fixture')
from app.commercial.pool08.payments import Payments
from app.commercial.pool08.payment_store import Store
from app.commercial.pool08.bold_gateway import BoldGateway
from app.commercial.pool08.crm import CRMError
from pool08_pricing_cases import PricingCases
class Checks(unittest.TestCase):
 def setUp(self):
  self.c=fixture['SagaChecks']();self.c.setUp();self.addCleanup(self.c.doCleanups);self.calls=[]
  values=PricingCases.values(self,unit_price='100.00')
  with patch.object(PricingCases,'values',return_value=values):ref=self.c.reviewed()
  self.sale=self.c.sales.command(self.c.body('confirm',ref,2,confirmed=True))['sale_id']
  self.gateway=BoldGateway('synthetic-only-identity','synthetic-only-secret',self.send);self.p=Payments(Store(self.c.crm.store),self.c.sales,lambda:self.gateway)
 def tearDown(self):self.c.tearDown()
 def send(self,body):self.calls.append(body);return {'payload':{'id':'sga-test-link','url':'https://checkout.bold.co/payment/sga-test','reference':body['reference']}}
 def body(self,operation='create',ref=None,revision=0,**data):
  import uuid
  return dict(request_id=str(uuid.uuid4()),operation=operation,payment_id=ref,expected_revision=revision,data=data)
 def test_persisted_source_amount_and_no_duplicate_dispatch(self):
  ref=self.p.command(self.body(sale_id=self.sale,confirmed=True))['payment_id'];body=self.body('checkout',ref,1,confirmed=True);r=self.p.command(body);self.assertEqual(r['amount'],'119.00');self.assertEqual(r['status'],'CHECKOUT_READY');self.assertTrue(self.p.command(body)['replayed']);self.assertEqual(len(self.calls),1);self.assertFalse(r['payment_verified']);self.assertFalse(r['ledger_written']);self.assertTrue(self.p.history(ref)['history_verified'])
 def test_response_unknown_is_retained_and_not_resent(self):
  ref=self.p.command(self.body(sale_id=self.sale,confirmed=True))['payment_id']
  def fail(body):self.calls.append(body);raise TimeoutError()
  self.gateway.sender=fail;r=self.p.command(self.body('checkout',ref,1,confirmed=True));self.assertEqual(r['status'],'UNKNOWN')
  with self.assertRaises(CRMError):self.p.command(self.body('checkout',ref,3,confirmed=True))
  self.p.command(self.body('recover',ref,3));self.assertEqual(len(self.calls),1)
 def test_browser_or_declared_signature_never_confirms_money(self):
  with self.assertRaises(CRMError):self.p.browser_return({'paid':True})
  with self.assertRaises(CRMError):self.p.confirm({'hash':'declared'})
if __name__=='__main__':unittest.main()
