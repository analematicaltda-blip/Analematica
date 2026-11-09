"""No simulated DIAN acceptance, plaintext log or invoice mutation through legacy adapters."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import date
from unittest.mock import Mock
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='dian_boundary_fixture')
from apps.core_erp.accounting.dian_readiness import inspect_readiness,DianIntegrationUnavailable
ROOT=Path(__file__).resolve().parents[3]
class DianBoundaryTests(unittest.TestCase):
 def profile(self):
  company=str(uuid.uuid4());return company,{'company_id':company,'supplier_nit':'900123456','resolution_number':'18760000001','prefix':'TEST','range_start':1,'range_end':100,'next_number':1,'valid_from':'2026-01-01','valid_until':'2026-12-31','environment':'HABILITACION','software_id':str(uuid.uuid4()),'test_set_id':'synthetic-test-set'}
 def test_configured_profile_never_claims_ready_or_accepted(self):
  company,profile=self.profile();r=inspect_readiness(company,profile,today=date(2026,11,8));self.assertTrue(r['public_configuration_valid']);self.assertFalse(r['ready_to_submit']);self.assertFalse(r['fiscal_accepted']);self.assertFalse(r['network_called']);self.assertNotIn(profile['supplier_nit'],str(r))
 def test_wrong_company_unknown_secret_and_missing_profile_block(self):
  company,profile=self.profile()
  for value in (None,{**profile,'company_id':str(uuid.uuid4())},{**profile,'pin':'never-store-secret'}):
   r=inspect_readiness(company,value);self.assertFalse(r['public_configuration_valid']);self.assertFalse(r['ready_to_submit']);self.assertNotIn('never-store-secret',str(r))
 def test_exhausted_expired_and_production_profiles_are_blocked(self):
  company,p=self.profile();p.update(next_number=101,valid_until='2025-01-01',environment='PRODUCCION');r=inspect_readiness(company,p,today=date(2026,11,8));self.assertIn('RESOLUTION_RANGE_EXHAUSTED_OR_INVALID',r['blocking_codes']);self.assertIn('RESOLUTION_NOT_CURRENT',r['blocking_codes']);self.assertIn('HABILITATION_REQUIRED_BEFORE_PRODUCTION',r['blocking_codes'])
 def test_legacy_facturacion_never_returns_fabricated_cufe_or_approval(self):
  module=runpy.run_path(str(ROOT/'BACKEND/SGA-ERP-TUR-BAKEND/facturacion/dian_service.py'));service=module['DIANIntegrationService'];invoice=Mock()
  for name in ('calculate_cufe','generate_ubl_xml','sign_and_send'):
   with self.assertRaises(DianIntegrationUnavailable):getattr(service,name)(invoice)
  invoice.assert_not_called();self.assertEqual(invoice.mock_calls,[])
 def test_commercial_dian_adapter_blocks_before_invoice_or_log_changes(self):
  module=runpy.run_path(str(ROOT/'BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/dian_services.py'));invoice=Mock()
  for name in ('procesar_envio_dian','generate_xml_dian','calculate_cufe','sign_invoice','send_to_dian'):
   with self.assertRaises(DianIntegrationUnavailable):getattr(module['FacturacionElectronicaService'],name)(invoice)
  with self.assertRaises(DianIntegrationUnavailable):module['DianService'].enviar_factura(invoice,Mock())
  self.assertEqual(invoice.mock_calls,[])
 def test_owner_scoped_api_returns_private_diagnosis(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  case=fixture['RecognitionTests']();case.setUp();request=APIRequestFactory().get('/fixture/',{'provider_id':str(case.case.provider.pk)});force_authenticate(request,user=case.case.actor)
  response=PlanCuentaViewSet.as_view({'get':'dian_readiness'})(request);self.assertEqual(response.status_code,200);self.assertEqual(response.data['company_id'],str(case.case.tenant.pk));self.assertIn('no-store',response['Cache-Control']);self.assertFalse(response.data['fiscal_accepted'])
if __name__=='__main__':unittest.main()
