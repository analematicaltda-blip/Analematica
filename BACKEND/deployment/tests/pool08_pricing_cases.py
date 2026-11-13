"""Shared behavioral cases; each runner exercises its own actual API and storage."""
import uuid,copy
from datetime import datetime,timezone,timedelta
class PricingCases:
 def body(self,operation='create',ref=None,revision=0,**data):return dict(request_id=str(uuid.uuid4()),operation=operation,item_id=ref,expected_revision=revision,data=data)
 def values(self,**changes):
  now=datetime.now(timezone.utc)
  value=dict(code='P'+uuid.uuid4().hex[:12].upper(),title='Servicio de prueba',kind='SERVICE',sector='Clasificación declarada',unit_price='12345.67',currency='COP',valid_from=(now-timedelta(days=1)).isoformat(),valid_until=(now+timedelta(days=30)).isoformat(),max_discount_bps=1000,terms='Condiciones de laboratorio no fiscales',tax=dict(name='IVA',treatment='TAXABLE',rate_bps=1900,policy_ref='POLITICA-SINTETICA-v1',support_digest='a'*64,review_reason='Revisión declarada de prueba'))
  value.update(changes);return value
 def create(self,**changes):
  r=self.call('post',self.body(**self.values(**changes)));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)['item_id']
 def offer(self,ref,revision=1,quantity='2',discount_bps=1000,**extra):
  line=dict(item_id=ref,revision=revision,quantity=quantity,discount_bps=discount_bps);line.update(extra);return self.body('estimate',currency='COP',lines=[line])
 def test_decimal_price_discount_and_tax_from_server(self):
  ref=self.create();r=self.call('post',self.offer(ref));self.assertEqual(r.status_code,200,self.data(r));e=self.data(r)['estimate'];self.assertEqual((e['subtotal'],e['discount'],e['tax'],e['total']),('24691.34','2469.13','4222.22','26444.43'));self.assertFalse(e['tax_acceptance_verified']);self.assertFalse(e['payment_verified']);self.assertFalse(e['ledger_written']);self.assertEqual(e['lines'][0]['unit_price'],'12345.67')
 def test_manipulated_price_and_total_rejected(self):
  ref=self.create()
  for key in ('unit_price','tax','total','currency'):
   r=self.call('post',self.offer(ref,**{key:'0.01'}));self.assertEqual(r.status_code,422,self.data(r))
 def test_invalid_money_types_precision_exponents_rejected(self):
  for value in (12.25,True,'1e3','NaN','-1.00','10.001','01.00','10000000000000000.00'):
   r=self.call('post',self.body(**self.values(unit_price=value)));self.assertEqual(r.status_code,422,self.data(r))
 def test_tax_rate_and_declared_review_sources(self):
  v=self.values();v['tax']['treatment']='EXEMPT';self.assertEqual(self.call('post',self.body(**v)).status_code,422)
  v['tax']['rate_bps']=0;r=self.call('post',self.body(**v));self.assertEqual(r.status_code,200,self.data(r));item=self.data(self.call(ref=self.data(r)['item_id']));self.assertFalse(item['tax_review']['professional_authorization_verified']);self.assertEqual(item['tax_review']['status'],'DECLARED_REVIEW');self.assertEqual(self.data(self.call('post',self.offer(item['id'],discount_bps=0)))['estimate']['tax'],'0.00')
 def test_discount_limits_and_quantity_validation(self):
  ref=self.create()
  for discount in (-1,1001,True,10.0):self.assertEqual(self.call('post',self.offer(ref,discount_bps=discount)).status_code,422)
  for q in ('0','-1','1e2','1.0001',1,'100001'):self.assertEqual(self.call('post',self.offer(ref,quantity=q)).status_code,422)
 def test_validity_and_inactive_prices(self):
  now=datetime.now(timezone.utc);ref=self.create(valid_from=(now-timedelta(days=2)).isoformat(),valid_until=(now-timedelta(days=1)).isoformat());self.assertEqual(self.call('post',self.offer(ref)).status_code,409)
  ref=self.create();self.assertEqual(self.call('post',self.body('deactivate',ref,1,reason='Retiro declarado')).status_code,200);self.assertEqual(self.call('post',self.offer(ref,2)).status_code,409);self.assertEqual(self.call('post',self.body('activate',ref,2,reason='Nueva vigencia revisada')).status_code,200);self.assertEqual(self.call('post',self.offer(ref,3)).status_code,200)
 def test_stale_revision_duplicate_code_and_cas(self):
  values=self.values();r=self.call('post',self.body(**values));ref=self.data(r)['item_id'];self.assertEqual(self.call('post',self.body(**values)).status_code,409);self.assertEqual(self.call('post',self.body('update',ref,1,unit_price='999.99')).status_code,200);self.assertEqual(self.call('post',self.body('update',ref,1,title='Conflicto')).status_code,409);self.assertEqual(self.call('post',self.offer(ref)).status_code,409);self.assertEqual(self.call('post',self.offer(ref,2)).status_code,200)
 def test_idempotent_commands_private_receipt_and_snapshot(self):
  body=self.body(**self.values());a=self.call('post',body);b=self.call('post',body);self.assertEqual(self.data(a)['item_id'],self.data(b)['item_id']);self.assertTrue(self.data(b)['replayed']);changed=copy.deepcopy(body);changed['data']['title']='Otra';self.assertEqual(self.call('post',changed).status_code,409)
  ref=self.data(a)['item_id'];body=self.offer(ref);one=self.data(self.call('post',body));self.call('post',self.body('update',ref,1,unit_price='999.99'));self.assertEqual(self.data(self.call('post',body))['estimate'],one['estimate']);receipt=self.data(self.call(ref=body['request_id'],section='receipt'));self.assertEqual(receipt['estimate'],one['estimate']);self.assertTrue(receipt['previous_receipt_only'])
 def test_multi_item_currency_scope_and_no_float_totals(self):
  ref=self.create(unit_price='0.01');b=self.offer(ref,quantity='0.5',discount_bps=0);self.assertEqual(self.data(self.call('post',b))['estimate']['total'],'0.01');other=self.create(currency='USD');b=self.offer(other,discount_bps=0);self.assertEqual(self.call('post',b).status_code,422)
  b=self.offer(ref);b['data']['lines']*=2;self.assertEqual(self.call('post',b).status_code,422)
 def test_history_retains_versions(self):
  ref=self.create();self.call('post',self.body('update',ref,1,unit_price='12.34'));self.call('post',self.body('deactivate',ref,2,reason='Revisión'));history=self.data(self.call(ref=ref,section='history'));self.assertTrue(history['history_verified']);self.assertEqual(len(history['events']),3);self.assertEqual(history['events'][0]['data']['unit_price'],'12345.67');self.assertEqual(history['events'][1]['data']['unit_price'],'12.34')
 def test_unknown_fields_invalid_tax_and_permanence(self):
  ref=self.create()
  for change in ({'payment_verified':True},{'unit_price':'0.00','arbitrary':True}):self.assertEqual(self.call('post',self.body('update',ref,1,**change)).status_code,422)
  v=self.values();v['tax']['support_digest']='x';self.assertEqual(self.call('post',self.body(**v)).status_code,422);self.assertEqual(self.data(self.call(ref=ref))['revision'],1)

 def test_tax_review_not_falsely_refreshed_and_context_changes_require_review(self):
  ref=self.create();initial=self.data(self.call(ref=ref));self.assertEqual(self.call('post',self.body('update',ref,1,unit_price='25.00')).status_code,200);new=self.data(self.call(ref=ref));self.assertEqual(initial['tax_review'],new['tax_review']);self.assertEqual(self.call('post',self.body('update',ref,2,kind='PRODUCT')).status_code,422);self.assertEqual(self.call('post',self.body('update',ref,2)).status_code,422)

 def test_offer_is_independent_of_ambient_decimal_traps_and_exponents(self):
  from decimal import localcontext,Inexact,Rounded,ROUND_DOWN
  ref=self.create()
  with localcontext() as ambient:
   ambient.prec=4;ambient.rounding=ROUND_DOWN;ambient.Emax=3;ambient.Emin=-3
   ambient.traps[Inexact]=True;ambient.traps[Rounded]=True
   response=self.call('post',self.offer(ref));self.assertEqual(response.status_code,200,self.data(response))
   estimate=self.data(response)['estimate'];self.assertEqual((estimate['subtotal'],estimate['discount'],estimate['tax'],estimate['total']),('24691.34','2469.13','4222.22','26444.43'))
   self.assertEqual(ambient.prec,4);self.assertEqual(ambient.Emax,3);self.assertTrue(ambient.traps[Inexact]);self.assertTrue(ambient.traps[Rounded])
