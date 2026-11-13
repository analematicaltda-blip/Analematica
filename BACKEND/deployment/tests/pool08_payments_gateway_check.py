"""Bold transport boundary with synthetic responses, no provider credentials or calls."""
import importlib.util,unittest,copy
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/commercial/pool08/bold_gateway.py';s=importlib.util.spec_from_file_location('bold_transport_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GatewayChecks(unittest.TestCase):
 def test_canonical_amounts_reject_float_boolean_exponent_and_precision(self):
  for bad in [True,12.0,'1e2','1.001','NaN','-1','0','01','1000000000000']:
   with self.subTest(value=str(bad)),self.assertRaises(m.GatewayError):m.amount(bad)
  self.assertEqual(m.amount('100.5'),'100.50')
 def test_success_requires_actual_response_and_does_not_expose_keys(self):
  g=m.BoldGateway('synthetic-identity','synthetic-secret',lambda body:{'payload':{'id':'link-1','url':'https://checkout.bold.co/payment/link-1','reference':body['reference']}});r=g.create('PAY-1','100.00','COP','Servicio');self.assertEqual(r['amount'],'100.00');self.assertFalse(r['payment_verified']);self.assertNotIn('secret',str(r));self.assertNotIn('identity',str(r))
 def test_no_fallback_link_after_timeout_or_invalid_response(self):
  for sender in [lambda p:(_ for _ in ()).throw(TimeoutError()),lambda p:{},lambda p:{'payload':{'id':'x','url':'https://attacker.invalid/pay'}}]:
   with self.assertRaises(m.GatewayError) as e:m.BoldGateway('i','s',sender).create('PAY-1','100','COP','Servicio')
   self.assertTrue(e.exception.uncertain)
 def test_fractional_pesos_never_truncate_or_send(self):
  calls=[]
  with self.assertRaises(m.GatewayError) as e:m.BoldGateway('i','s',lambda body:calls.append(body)).create('PAY-1','100.50','COP','Servicio')
  self.assertEqual(calls,[]);self.assertFalse(e.exception.uncertain)
 def test_declared_hash_and_json_never_confirm_payment(self):
  with self.assertRaises(m.GatewayError):m.BoldGateway('i','s').verify_webhook({'paid':True},'declared-hash')
 def test_missing_credentials_never_attempt_network(self):
  calls=[]
  with self.assertRaises(m.GatewayError):m.BoldGateway(sender=lambda body:calls.append(body)).create('PAY-1','100','COP','Servicio')
  self.assertEqual(calls,[])
if __name__=='__main__':unittest.main()
