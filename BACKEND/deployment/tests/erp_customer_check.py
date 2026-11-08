"""ERP CRM round trips against isolated tables, without external providers."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('provider_security_check.py')),run_name='fixture_setup')
fixture['ProviderChecks'].setUpClass()
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_comercial.views import ClienteViewSet
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.views import ClienteViewSet as OperationalClientes
from rest_framework.test import APIRequestFactory,force_authenticate
fixture['create'](Cliente)
from types import SimpleNamespace
F=SimpleNamespace(**{key:getattr(fixture['ProviderChecks'],key) for key in ['owner','other','customer','p','q']})
class CustomerChecks(unittest.TestCase):
 def request(self,view,action,user,method='get',data=None,pk=None):
  request=getattr(APIRequestFactory(),method)('/isolated/',data or {},format='json');force_authenticate(request,user=user)
  return view.as_view({method:action})(request,**({'pk':pk} if pk else {}))
 def test_create_read_update_isolated_between_companies(self):
  r=self.request(ClienteViewSet,'create',F.owner,'post',{'nombre':'Synthetic client','email':'crm@example.test','telefono':'123','perfil_ref_id':str(F.q.pk),'perfil':str(F.q.pk)})
  self.assertEqual(r.status_code,201,r.data);pk=r.data['id'];client=Cliente.objects.get(pk=pk)
  self.assertEqual(client.perfil_id,F.p.pk);self.assertIsNotNone(client.id_publico)
  self.assertEqual(self.request(ClienteViewSet,'retrieve',F.other,pk=pk).status_code,404)
  self.assertEqual(self.request(ClienteViewSet,'partial_update',F.other,'patch',{'nombre':'Injected'},pk).status_code,404)
  self.assertEqual(self.request(ClienteViewSet,'partial_update',F.owner,'patch',{'nombre':'Updated'},pk).status_code,200)
  self.assertEqual(self.request(OperationalClientes,'retrieve',F.owner,pk=pk).data['nombre'],'Updated')
 def test_missing_provider_is_denied(self):
  self.assertEqual(self.request(ClienteViewSet,'list',F.customer).status_code,403)
 def test_duplicate_email_same_company_is_rejected(self):
  data={'nombre':'Duplicate','email':'duplicate@example.test'}
  self.assertEqual(self.request(ClienteViewSet,'create',F.other,'post',data).status_code,201)
  self.assertEqual(self.request(ClienteViewSet,'create',F.other,'post',data).status_code,400)
 def test_forged_tenant_context_cannot_access_other_company(self):
  target='apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions.get_current_tenant'
  with patch(target,return_value=F.q):self.assertEqual(self.request(ClienteViewSet,'list',F.owner).status_code,403)
 def test_unverified_commercial_workflow_cannot_write_or_report_fake_totals(self):
  from apps.prestadores.mi_negocio.gestion_comercial.views import OperacionComercialViewSet,POSView
  from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial
  with patch.object(OperacionComercial.objects,'create',side_effect=AssertionError('must not create sale')):
   for action,method in [('list','get'),('stats','get'),('create','post'),('partial_update','patch'),('destroy','delete')]:
    response=self.request(OperacionComercialViewSet,action,F.owner,method,{'total':'1','perfil_ref_id':str(F.q.pk)},pk=str(uuid.uuid4()) if action in ('partial_update','destroy') else None)
    self.assertEqual(response.status_code,503,response.data)
   request=APIRequestFactory().post('/isolated/',{'total':'1'},format='json');force_authenticate(request,user=F.owner)
   response=POSView.as_view()(request);self.assertEqual(response.status_code,503);self.assertNotIn('factura',response.data)
 def test_unverified_sales_still_require_authentication(self):
  from apps.prestadores.mi_negocio.gestion_comercial.views import OperacionComercialViewSet,POSView
  request=APIRequestFactory().post('/isolated/',{'total':'1'},format='json')
  self.assertIn(POSView.as_view()(request).status_code,(401,403))
  self.assertIn(OperacionComercialViewSet.as_view({'post':'create'})(request).status_code,(401,403))
if __name__=='__main__':unittest.main()
