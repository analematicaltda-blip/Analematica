import runpy,unittest,importlib
from pathlib import Path
from pool08_ads_cases import AdsCases
f=runpy.run_path(str(Path(__file__).with_name('pool08_generation_native_check.py')),run_name='campaign_native_setup')
from django.db import connection
for path in ['apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08']:
 m=importlib.import_module(path+'.ads_models');publication=importlib.import_module(path+'.publishing_models')
 with connection.schema_editor() as e:
  for model in (publication.PublishingRecord,publication.PublishingEvent,m.AdsRecord,m.AdsEvent):
   if model._meta.db_table not in connection.introspection.table_names():e.create_model(model)
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:
 base=f['cases'](system,path)
 class Checks(AdsCases,base):pass
 suite.addTests(Checks(n) for n in unittest.defaultTestLoader.getTestCaseNames(AdsCases))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
