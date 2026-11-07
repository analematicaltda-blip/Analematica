"""Wallet contracts using isolated real models; no actual money or provider calls."""
import runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('provider_security_check.py')),run_name='fixture_setup')
fixture['ProviderChecks'].setUpClass()
F=SimpleNamespace(**{name:getattr(fixture['ProviderChecks'],name) for name in ['owner','other','customer']})
from django.test import override_settings
from django.utils import timezone
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework.exceptions import APIException
from django.http import Http404
from rest_framework.test import APIRequestFactory,force_authenticate,APIClient
from apps.wallet.models import Wallet,WalletMovimiento,WalletTransaccion,WalletTransferIntent,WalletLimiteOperativo
from apps.wallet.services import internal_transfer as engine
from apps.wallet.services.wallet_service import WalletService
from apps.wallet.views import WalletAccountViewSet,WalletTransactionViewSet,WalletTransferViewSet
for model in [WalletMovimiento,WalletTransferIntent,WalletLimiteOperativo]:fixture['create'](model)

class WalletChecks(unittest.TestCase):
 def setUp(self):
  override=override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=True);override.enable();self.addCleanup(override.disable)
  self.source=Wallet.objects.create(user_id=F.owner.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP',saldo_disponible='100.00')
  self.target=Wallet.objects.create(user_id=F.other.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP')
  WalletLimiteOperativo.objects.create(wallet=self.source,monto_maximo_transaccion='40',monto_maximo_diario='60')
 def prepare(self,amount='10',key=None):return engine.prepare(F.owner,self.source.pk,self.target.pk,amount,key or uuid.uuid4())
 def approved(self,amount='10'):
  intent=self.prepare(amount);intent,token=engine.review(F.owner,intent.pk,intent.digest);return intent,token
 def balances(self):
  self.source.refresh_from_db();self.target.refresh_from_db();return self.source.saldo_disponible,self.target.saldo_disponible
 def call(self,view,action,user,method='get',pk=None,data=None):
  req=getattr(APIRequestFactory(),method)('/isolated/',data or {},format='json');force_authenticate(req,user=user)
  return view.as_view({method:action})(req,**({'pk':pk} if pk else {}))
 def test_two_approvals_balance_and_replay(self):
  intent=self.prepare();self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
  with self.assertRaises(APIException):engine.execute(F.owner,intent.pk,intent.digest,'x'*40)
  intent,token=engine.review(F.owner,intent.pk,intent.digest);self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
  result=engine.execute(F.owner,intent.pk,intent.digest,token);self.assertEqual(self.balances(),(Decimal('90'),Decimal('10')))
  replay=engine.execute(F.owner,intent.pk,intent.digest,token);self.assertEqual(result.transaction_id,replay.transaction_id);self.assertEqual(self.balances(),(Decimal('90'),Decimal('10')))
  movements=list(result.transaction.movimientos.all());self.assertEqual(len(movements),2);self.assertEqual(movements[0].monto,movements[1].monto)
  for movement in movements:self.assertEqual(movement.hash_integridad,movement.integrity_digest())
 def test_invalid_amounts(self):
  for value in ['0','-1','NaN','Infinity','1.001','999999999999999999999']:
   with self.subTest(value=value),self.assertRaises(APIException):self.prepare(value)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
 def test_idempotency_content_is_bound(self):
  key=uuid.uuid4();a=self.prepare(key=key);self.assertEqual(a.pk,self.prepare(key=key).pk)
  with self.assertRaises(engine.TransferConflict):self.prepare('11',key)
 def test_foreign_actor_and_digest_rejected(self):
  intent=self.prepare()
  with self.assertRaises(Http404):engine.review(F.other,intent.pk,intent.digest)
  with self.assertRaises(APIException):engine.review(F.owner,intent.pk,'0'*64)
  with self.assertRaises(Http404):engine.prepare(F.other,self.source.pk,self.target.pk,'10',uuid.uuid4())
 def test_confirmation_token_not_stored_plaintext(self):
  intent,token=self.approved();self.assertNotEqual(intent.confirmation_hash,token)
  with self.assertRaises(APIException):engine.execute(F.owner,intent.pk,intent.digest,'z'*40)
  with self.assertRaises(APIException):engine.review(F.owner,intent.pk,intent.digest)
 def test_expiration_and_changed_wallet_state(self):
  intent,token=self.approved();WalletTransferIntent.objects.filter(pk=intent.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
  with self.assertRaises(APIException):engine.execute(F.owner,intent.pk,intent.digest,token)
  intent,token=self.approved();self.target.estado='BLOQUEADO';self.target.save()
  with self.assertRaises(APIException):engine.execute(F.owner,intent.pk,intent.digest,token)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
 def test_currency_limits_and_negative_balance(self):
  self.target.currency='USD';self.target.save()
  with self.assertRaises(APIException):self.prepare()
  self.target.currency='COP';self.target.save()
  with self.assertRaises(APIException):self.prepare('41')
  self.source.saldo_disponible=Decimal('2');self.source.save()
  with self.assertRaises(APIException):self.prepare()
 def test_daily_limit_and_additional_governance(self):
  limit=self.source.limite;limit.monto_maximo_diario=Decimal('15');limit.save()
  intent,token=self.approved();engine.execute(F.owner,intent.pk,intent.digest,token)
  with self.assertRaises(APIException):self.prepare()
  limit.requiere_aprobacion_soberana=True;limit.save()
  with self.assertRaises(APIException):self.prepare('1')
 def test_atomic_rollback_on_ledger_failure(self):
  intent,token=self.approved()
  with patch.object(WalletMovimiento.objects,'create',side_effect=RuntimeError('synthetic storage failure')):
   with self.assertRaises(RuntimeError):engine.execute(F.owner,intent.pk,intent.digest,token)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')));intent.refresh_from_db();self.assertEqual(intent.state,'REVIEWED');self.assertIsNone(intent.transaction_id)
 def test_feature_off_and_non_administrator(self):
  with override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=False),self.assertRaises(APIException):self.prepare()
  with self.assertRaises(APIException):engine.prepare(F.customer,self.source.pk,self.target.pk,'10',uuid.uuid4())
 def test_legacy_services_cannot_create_or_refund_funds(self):
  service=WalletService(F.owner)
  for method in ['deposit','pay','execute_complex_transaction','release_payment','refund','liquidate','authorize_payment','cancel_authorization','freeze','pay_to_user']:
   with self.subTest(method=method),self.assertRaises(APIException):getattr(service,method)()
  self.assertEqual(self.call(WalletAccountViewSet,'deposit',F.owner,'post',self.target.pk).status_code,404)
  self.assertEqual(self.call(WalletAccountViewSet,'deposit',F.owner,'post',self.source.pk).status_code,503)
  from apps.wallet.handlers import WalletEventHandlers
  with self.assertRaises(APIException):WalletEventHandlers.handle_payment_request({'customer_id':F.owner.pk,'amount':'10'})
  from apps.wallet.admin import WalletAdmin
  from django.contrib import admin
  model_admin=WalletAdmin(Wallet,admin.site)
  self.assertFalse(model_admin.has_add_permission(None));self.assertFalse(model_admin.has_change_permission(None));self.assertFalse(model_admin.has_delete_permission(None))
  from apps.wallet.agents.soldados import SoldadoAuditor,SoldadoAnalista,SoldadoVigilante
  for cls in [SoldadoAuditor,SoldadoAnalista,SoldadoVigilante]:
   agent=cls.__new__(cls);agent.soldier_id='synthetic';self.assertEqual(agent.perform_action({})['status'],'NOT_IMPLEMENTED')
  from apps.wallet.agents.sargentos import SargentoOperacionBalance,SargentoRegistroMovimiento,SargentoBitacoraSoberana,SargentoEscrituraContable
  for cls in [SargentoOperacionBalance,SargentoRegistroMovimiento,SargentoBitacoraSoberana,SargentoEscrituraContable]:
   with self.assertRaises(APIException):cls().execute({})
 def test_movement_is_immutable_and_counterparty_metadata_private(self):
  intent,token=self.approved();result=engine.execute(F.owner,intent.pk,intent.digest,token)
  movement=result.transaction.movimientos.first()
  with self.assertRaises(ModelValidationError):movement.save()
  response=self.call(WalletTransactionViewSet,'retrieve',F.other,pk=result.transaction_id)
  self.assertEqual(response.status_code,200);self.assertEqual(len(response.data['movimientos']),1);self.assertNotIn('metadata',response.data)
  self.assertEqual(str(response.data['movimientos'][0]['wallet']),str(self.target.pk))
 def test_read_only_http_cannot_reassign_wallet_owner(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(F.owner)
  route='/api/v1/finance/wallet/accounts/'
  self.assertEqual(client.post(route,{'user_id':F.other.pk},format='json').status_code,405)
  self.assertEqual(client.patch(route+str(self.source.pk)+'/',{'user_id':F.other.pk},format='json').status_code,405)
 def test_transfer_http_requires_separate_review_and_execute(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(F.owner)
  route='/api/v1/finance/wallet/transfers/'
  r=client.post(route,{'source':str(self.source.pk),'destination':str(self.target.pk),'amount':'10.00','idempotency_key':str(uuid.uuid4())},format='json')
  self.assertEqual(r.status_code,201,r.content);intent=r.json()['data'];detail=route+intent['id']+'/'
  review=client.post(detail+'review/',{'digest':intent['digest']},format='json');self.assertEqual(review.status_code,200,review.content)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
  confirmation=review.json()['data']['confirmation'];self.assertNotIn('confirmation',client.get(detail).json()['data'])
  r=client.post(detail+'execute/',{'digest':intent['digest'],'confirmation':confirmation},format='json');self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(r['Cache-Control'],'no-store');self.assertEqual(self.balances(),(Decimal('90'),Decimal('10')))
 def test_database_error_reports_unknown_outcome_without_sql_details(self):
  from django.db import OperationalError
  with patch.object(engine,'prepare',side_effect=OperationalError('private SQL and credentials')):
   r=self.call(WalletTransferViewSet,'create',F.owner,'post',data={'source':str(self.source.pk),'destination':str(self.target.pk),'amount':'10','idempotency_key':str(uuid.uuid4())})
  self.assertEqual(r.status_code,503);self.assertNotIn('private SQL',str(r.data));self.assertIn('idempotencia',str(r.data))
if __name__=='__main__':unittest.main()
