"""Cross-provider media and canonical/index integrity regressions in actual native adapters."""
import runpy,unittest,importlib,uuid,hashlib
from pathlib import Path
from types import SimpleNamespace
f=runpy.run_path(str(Path(__file__).with_name('pool08_quotations_native_check.py')),run_name='audit_native_setup')
from django.db import connection
for p in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 m=importlib.import_module(p+'.opportunity_models')
 with connection.schema_editor() as editor:
  for model in (m.CommercialOpportunity,m.OpportunityEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 error=importlib.import_module(path+'.crm').CRMError;digest=importlib.import_module(path+'.crm').digest
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=f['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups);self.base=SimpleNamespace(scope=str(self.c.base.tenant.pk),provider=str(self.c.base.provider.pk),transaction=lambda:None,lock=lambda:None)
  def test_media_is_not_visible_to_other_provider_in_same_company(self):
   store=importlib.import_module(path+'.quotation_store').Store(self.base);rid=str(uuid.uuid4());data=b'PRIVATE-PROVIDER-A';sha=hashlib.sha256(data).hexdigest();store.save_asset(rid,str(self.c.base.user.pk),data,'image/png',sha,sha)
   other=importlib.import_module(path+'.quotation_store').Store(SimpleNamespace(**{**self.base.__dict__,'provider':str(uuid.uuid4())}));self.assertIsNone(other.asset(rid));self.assertEqual(other.asset_usage(),(0,0));self.assertEqual(store.asset(rid)['data'],data)
  def test_legacy_unscoped_media_is_preserved_but_quarantined(self):
   module=importlib.import_module(path+'.quotation_models');ref=str(uuid.uuid4());data=b'LEGACY-UNATTRIBUTED';sha=hashlib.sha256(data).hexdigest()
   module.QuotationAsset.objects.create(id=ref,scope=self.base.scope,creator_ref=str(self.c.base.user.pk),data=data,mime='image/png',digest=sha,original_digest=sha)
   store=importlib.import_module(path+'.quotation_store').Store(self.base)
   self.assertIsNone(store.asset(ref));self.assertEqual(store.asset_usage(),(0,0));self.assertEqual(bytes(module.QuotationAsset.objects.get(pk=ref).data),data)
  def test_price_quote_and_sale_indices_cannot_disagree_with_document(self):
   from django.db import connection
   for domain,modelname,prefix in [('pricing','CommercialPrice','PRICE'),('quotation','CommercialQuotation','QUOTE'),('sales','CommercialSale','SALE')]:
    module=importlib.import_module(path+'.'+domain+'_models');model=getattr(module,modelname)
    with connection.schema_editor() as editor:
     for name in (modelname,{'pricing':'PriceEvent','quotation':'QuotationEvent','sales':'SaleEvent'}[domain]):
      cls=getattr(module,name)
      if cls._meta.db_table not in connection.introspection.table_names():editor.create_model(cls)
    ref=str(uuid.uuid4());doc={'id':ref,'revision':1,'code':'CODE-'+ref,'status':'DRAFT','title':'Canonical'};model.objects.create(id=ref,scope=self.base.scope,provider_ref=self.base.provider,revision=1,code=doc['code'],status='DRAFT',document=doc,document_digest=digest(doc));store=importlib.import_module(path+'.'+domain+'_store').Store(self.base)
    for field,value in [('revision',2),('status','OTHER'),('code','OTHER')]:
     model.objects.filter(pk=ref).update(**{field:value})
     with self.assertRaises(error) as caught:store.get(ref)
     self.assertEqual(caught.exception.status,503)
     if field=='code':
      with self.assertRaises(error):store.find_code(doc['code'])
     model.objects.filter(pk=ref).update(**{field:doc[field]})
    self.assertEqual(store.get(ref)['id'],ref)
 Checks.__name__=system.replace('-','')+'Audit';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
