"""Actual native ORM event routing/index corruption across eight commercial domains."""
import importlib,runpy,unittest
from pathlib import Path
from django.db import models
from pool08_event_cases import EventBindingCases,DOMAINS
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_audit_native_check.py')),run_name='event_native_setup')
from django.db import connection

def cases(system,path,domain,modelname):
    module=importlib.import_module(path+'.'+domain+'_models');model=getattr(module,modelname)
    with connection.schema_editor() as editor:
        for cls in vars(module).values():
            if isinstance(cls,type) and issubclass(cls,models.Model) and not cls._meta.abstract and cls._meta.db_table not in connection.introspection.table_names():editor.create_model(cls)
    class Checks(EventBindingCases,unittest.TestCase):
        def setUp(self):
            self.c=fixture['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups)
            self.base=self.c.base
            if domain=='opportunity' and system=='erp-tur':
                legacy=importlib.import_module('apps.prestadores.mi_negocio.gestion_comercial.sales.models')
                with connection.schema_editor() as editor:
                    for cls in (legacy.Opportunity,legacy.StageHistory):
                        if cls._meta.db_table not in connection.introspection.table_names():editor.create_model(cls)

            self.store=importlib.import_module(path+'.'+domain+'_store').Store(self.base)
            self.error=importlib.import_module(path+'.crm').CRMError;self.digest=importlib.import_module(path+'.crm').digest
            self.domain=domain;self.item_field='opportunity' if domain=='opportunity' else 'item_id'
        def insert(self,rid,item,doc):model.objects.create(id=rid,scope=self.base.scope,**{self.item_field:item},document=doc)
        def update(self,rid,**values):model.objects.filter(id=rid).update(**values)
    return Checks
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:
 for domain,model in DOMAINS:globals()[system.replace('-','')+'_'+domain]=cases(system,path,domain,model)
if __name__=='__main__':unittest.main()
