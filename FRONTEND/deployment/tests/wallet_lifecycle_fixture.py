"""Opt-in disposable browser setup. Never imported by application code."""
def apply(case,reservation,create):
 import uuid
 from datetime import timedelta
 from django.conf import settings
 from django.utils import timezone
 from apps.wallet.models import Wallet,WalletTransferIntent,WalletLimiteOperativo,WalletMovimiento,WalletDeviceChallenge
 from apps.wallet.services.company_administrator import TourismCompanyAdministrator
 from apps.core_erp.accounting.models import Account,LedgerEntry
 from apps.core_erp.accounting.ledger_engine import LedgerEngine
 from apps.prestadores.mi_negocio.gestion_comercial import cancellation_policies as policy,wallet_refund as refund
 for model in (Wallet,WalletTransferIntent,WalletLimiteOperativo,WalletMovimiento,WalletDeviceChallenge):create(model)
 asset=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='1199-LIFE',name='Synthetic wallet asset',type='ASSET');owed=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='2399-LIFE',name='Synthetic customer refund payable',type='LIABILITY')
 funding=LedgerEngine.post_lines(tenant_id=case.tenant.pk,entry_date=timezone.localdate(),description='Synthetic funded wallet and net refund obligation',lines_data=[{'account':asset,'debit':'100.00'},{'account':owed,'credit':'90.00'},{'account':case.b,'credit':'10.00'}],actor=case.user,idempotency_key='wallet-lifecycle-fixture')
 line=LedgerEntry.plain_objects.get(journal_entry=funding,account=owed)
 from django.contrib.auth import get_user_model
 recipient=get_user_model().objects.filter(is_active=True).exclude(pk=case.user.pk).first()
 source=Wallet.objects.create(owner_type='CORPORATIVO',owner_id=str(case.tenant.pk),currency='COP',saldo_disponible='100.00',metadata={'accounting_asset_account_id':str(asset.pk)})
 destination=Wallet.objects.create(owner_type='TURISTA',owner_id=str(uuid.uuid4()),user_id=recipient.pk,currency='COP',metadata={'wallet_signup':True});WalletLimiteOperativo.objects.create(wallet=source,monto_maximo_transaccion='100.00',monto_maximo_diario='100.00')
 def verifier(company,booking,wallet):
  now=timezone.now();return refund.VerifiedRefundBeneficiary(company_id=company.pk,customer_id=reservation.customer_id,wallet_id=destination.pk,user_id=recipient.pk,reservation_id=reservation.pk,accepts_wallet_refund=True,evidence_digest='f'*64,checked_at=now,valid_until=now+timedelta(minutes=2))
 verifier.wallet_id=lambda company,booking:destination.pk
 settings.WALLET_INTERNAL_TRANSFERS_ENABLED=True;settings.WALLET_COMMERCIAL_REFUNDS_ENABLED=True;settings.WALLET_DEVICE_APPROVALS_REQUIRED=True;settings.WALLET_COMPANY_ADMIN_VERIFIER=TourismCompanyAdministrator();settings.WALLET_REFUND_BENEFICIARY_VERIFIER=verifier
 scope={'actor':case.user,'provider_id':case.provider.pk};rid=str(reservation.pk);day=timezone.localdate().isoformat();values={'name':'Synthetic lifecycle policy','terms':'Synthetic accepted terms; not legal certification.','scope':'SERVICIO','percentage':'10.00','basis':'REQUESTED_REFUND','active':True,'valid_from':day,'valid_until':day}
 review=policy.review_policy(**scope,request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=values,confirmed=True);published=policy.publish_policy(**scope,review_id=review['review_id'],confirmed=True)
 policy.bind_policy(**scope,reservation_id=rid,policy_id=published['policy_id'],policy_revision=1,accepted_at=timezone.now().isoformat(),consent_kind='ACCEPTED_AMENDMENT',consent_digest='a'*64,confirmed=True)
 review=policy.review_case(**scope,reservation_id=rid,request_id=str(uuid.uuid4()),requested_refund='100.00',reason_code='STANDARD_CANCELLATION',evidence_digest='b'*64,expected_revision=0,confirmed=True);policy.confirm_case(**scope,reservation_id=rid,review_id=review['review_id'],confirmed=True)
 prepared=refund.prepare_wallet_refund(**scope,reservation_id=rid,source_wallet_id=str(source.pk),destination_wallet_id=str(destination.pk),liability_line_id=str(line.pk),evidence_digest='c'*64,confirmed=True)
 WalletTransferIntent.objects.filter(pk=prepared['binding']['intent_id']).update(expires_at=timezone.now()-timedelta(seconds=1))
