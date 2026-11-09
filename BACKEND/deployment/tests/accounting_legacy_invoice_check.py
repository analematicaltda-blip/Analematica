"""Actual legacy invoice ORM/DRF isolation and no plaintext document serialization."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='legacy_invoice_fixture')
from apps.domain_business.comercial.models import CommercialOperation
from apps.prestadores.mi_negocio.gestion_comercial.models.FacturaElectronica import FacturaElectronica
from apps.prestadores.mi_negocio.gestion_comercial.views_factura import FacturaViewSet
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
fixture['create'](FacturaElectronica)
class LegacyInvoiceTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.owner=self.case.case.actor;self.company=self.case.case.tenant;self.provider=self.case.case.provider
  self.other=fixture['RecognitionTests']();self.other.setUp()
  stranger=type(self.owner)(username='legacy-other-'+uuid.uuid4().hex,role='BUSINESS_OWNER',is_active=True);type(self.owner).objects.bulk_create([stranger]);type(self.provider).objects.filter(pk=self.other.case.provider.pk).update(owner=stranger)
  self.invoice=self.create_invoice(self.company,self.company)
  self.foreign=self.create_invoice(self.other.case.tenant,self.other.case.tenant)
  self.mismatch=self.create_invoice(self.company,self.other.case.tenant)
 def create_invoice(self,header_company,operation_company):
  operation=CommercialOperation.plain_objects.create(tenant=operation_company,customer_id=uuid.uuid4(),status='CONFIRMED',total='100.00')
  return FacturaElectronica.objects.create(tenant_id=str(header_company.pk),operacion_comercial=operation,cufe=uuid.uuid4().hex,xml_content='<PRIVATE-FISCAL-DOCUMENT/>',pdf_url='https://private.example.test/invoice.pdf',codigo_respuesta_dian='legacy-unverified',prestador_email='synthetic-owner@example.test',estado_dian='aceptada')
 def call(self,action='list',user=None,provider=None,pk=None,method='get'):
  request=getattr(APIRequestFactory(),method)('/fixture/',{'provider_id':str(provider or self.provider.pk)} if method=='get' else {},format='json')
  if method=='post':request=APIRequestFactory().post('/fixture/?provider_id='+str(provider or self.provider.pk),{},format='json')
  if user is not False:force_authenticate(request,user=user or self.owner)
  return FacturaViewSet.as_view({method:action})(request,**({'pk':str(pk)} if pk else {}))
 def test_owner_list_only_invoices_with_both_tenant_sides_verified(self):
  response=self.call();self.assertEqual(response.status_code,200,response.data);data=response.data.get('results') if isinstance(response.data,dict) else response.data
  self.assertEqual([row['id'] for row in data],[str(self.invoice.pk)])
 def test_document_plaintext_and_public_links_are_not_serialized(self):
  response=self.call('retrieve',pk=self.invoice.pk);self.assertEqual(response.status_code,200,response.data)
  self.assertNotIn('xml_content',response.data);self.assertNotIn('pdf_url',response.data);self.assertNotIn('PRIVATE-FISCAL-DOCUMENT',str(response.data));self.assertFalse(response.data['fiscal_acceptance_verified']);self.assertEqual(response.data['estado_dian'],'aceptada')
 def test_foreign_and_mismatched_invoice_details_are_not_found(self):
  for invoice in (self.foreign,self.mismatch):self.assertEqual(self.call('retrieve',pk=invoice.pk).status_code,404)
 def test_foreign_provider_and_revoked_binding_denied(self):
  self.assertEqual(self.call(provider=self.other.case.provider.pk).status_code,403)
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  self.assertEqual(self.call().status_code,403)
 def test_anonymous_denied_and_all_responses_private(self):
  self.assertIn(self.call(user=False).status_code,(401,403))
  for response in (self.call(),self.call('retrieve',pk=self.foreign.pk),self.call(user=False)):
   self.assertIn('no-store',response['Cache-Control'])
 def test_pdf_and_submission_never_return_fabricated_documents_or_acceptance(self):
  self.assertEqual(self.call('pdf',pk=self.foreign.pk).status_code,404)
  pdf=self.call('pdf',pk=self.invoice.pk);self.assertEqual(pdf.status_code,503);self.assertNotIn('PDF dummy',str(pdf.data))
  submitted=self.call('trigger_dian',method='post');self.assertEqual(submitted.status_code,503);self.assertFalse(submitted.data['fiscal_accepted']);self.assertFalse(submitted.data['network_called'])
 def test_draft_and_confirmed_operations_are_preserved_without_fake_invoice(self):
  for state in ('DRAFT','CONFIRMED'):
   operation=CommercialOperation.plain_objects.create(tenant=self.company,customer_id=uuid.uuid4(),status=state,total='100.00')
   self.assertTrue(CommercialOperation.plain_objects.filter(pk=operation.pk,status=state).exists());self.assertFalse(FacturaElectronica.objects.filter(operacion_comercial=operation).exists())
if __name__=='__main__':unittest.main()
