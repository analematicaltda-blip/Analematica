"""Authorization regressions; isolated database, no external identity or funds."""
import runpy, unittest, uuid
from pathlib import Path
from datetime import timedelta
from types import SimpleNamespace
fixture=runpy.run_path(str(Path(__file__).resolve().parents[2]/'BACKEND/deployment/tests/provider_security_check.py'),run_name='fixture_setup')
fixture['ProviderChecks'].setUpClass()
from django.test import override_settings
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from apps.wallet.models import Wallet
from apps.wallet.services import access_policy as policy
from django.apps import apps
for model in apps.get_app_config('wallet').get_models():fixture['create'](model)
F=SimpleNamespace(**{name:getattr(fixture['ProviderChecks'],name) for name in ('owner','other','customer')})
class AccessChecks(unittest.TestCase):
 def setUp(self):
  Wallet.objects.all().delete()
  self.user=F.customer
  self.company=Wallet.objects.create(user_id=self.user.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()))
 def proof(self,**changes):
  data=dict(user_id=self.user.pk,wallet_id=self.company.pk,company_reference=self.company.owner_id,platform='ERP_TUR',role='COMPANY_ADMINISTRATOR',evidence_digest='a'*64,checked_at=timezone.now(),valid_until=timezone.now()+timedelta(minutes=1));data.update(changes)
  return policy.VerifiedCompanyAdministrator(**data)
 def test_public_user_explicit_opt_in_does_not_activate_money(self):
  self.assertFalse(policy.personal_signup(self.user));w=policy.register_personal_profile(self.user)
  self.assertTrue(policy.personal_signup(self.user));self.assertEqual(w.estado,'SUSPENDIDO');self.assertFalse(w.currency);self.assertEqual(w.saldo_disponible,0)
  self.assertEqual(list(policy.accessible_wallets(self.user)),[w])
 def test_company_user_id_and_global_superuser_do_not_grant_access(self):
  for user in (self.user,F.owner):
   self.assertFalse(policy.company_access(user,self.company))
   with self.assertRaises(PermissionDenied):policy.require_wallet_access(user,self.company)
 def test_verified_primary_administrator_is_bound_to_company(self):
  self.assertTrue(policy.company_access(self.user,self.company,lambda *args:self.proof()))
  for change in ({'role':'ACCOUNTING_STAFF'},{'platform':'OTHER'},{'user_id':F.other.pk},{'wallet_id':uuid.uuid4()},{'company_reference':'other'},{'evidence_digest':'yes'}):
   self.assertFalse(policy.company_access(self.user,self.company,lambda *args:self.proof(**change)))
 def test_expired_or_client_dictionary_cannot_authorize(self):
  for proof in (self.proof(valid_until=timezone.now()-timedelta(seconds=1)),self.proof(checked_at=timezone.now()-timedelta(minutes=6)),{'role':'COMPANY_ADMINISTRATOR'},True):
   self.assertFalse(policy.company_access(self.user,self.company,lambda *args:proof))
 def test_discovery_rechecks_role_and_revocation(self):
  parent=self
  class Adapter:
   allowed=True
   def wallet_ids(self,user):return [parent.company.pk]
   def __call__(self,*args):return parent.proof(role='COMPANY_ADMINISTRATOR' if self.allowed else 'STAFF')
  adapter=Adapter()
  with override_settings(WALLET_COMPANY_ADMIN_VERIFIER=adapter):
   self.assertEqual(list(policy.accessible_wallets(self.user)),[self.company]);policy.require_wallet_access(self.user,self.company)
   adapter.allowed=False
   self.assertFalse(policy.accessible_wallets(self.user).exists())
   with self.assertRaises(PermissionDenied):policy.require_wallet_access(self.user,self.company)
 def test_another_person_cannot_read_personal_profile(self):
  w=policy.register_personal_profile(self.user)
  with self.assertRaises(PermissionDenied):policy.require_wallet_access(F.other,w)
 def test_generic_django_admin_has_no_wallet_access(self):
  from apps.wallet.admin import WalletAdmin
  from django.contrib import admin
  instance=WalletAdmin(Wallet,admin.site);request=SimpleNamespace(user=F.owner)
  self.assertFalse(instance.has_view_permission(request));self.assertFalse(instance.get_queryset(request).exists())
if __name__=='__main__':unittest.main()
