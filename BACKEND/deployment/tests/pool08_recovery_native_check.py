import runpy,unittest,importlib
from pathlib import Path
from pool08_operations_cases import OperationsCases
from pool08_recovery_cases import RecoveryCases
f=runpy.run_path(str(Path(__file__).with_name('pool08_generation_native_check.py')),run_name='campaign_native_setup')
from django.db import connection
for path in ['apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08']:
 m=importlib.import_module(path+'.army_models');publication=importlib.import_module(path+'.publishing_models')
 with connection.schema_editor() as e:
  for model in (publication.PublishingRecord,publication.PublishingEvent,m.ArmyRecord,m.ArmyEvent):
   if model._meta.db_table not in connection.introspection.table_names():e.create_model(model)
for path in ['apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08']:
 for module,classes in [('opportunity_models',('CommercialOpportunity','OpportunityEvent')),('email_campaign_models',('EmailCampaignRecord','EmailCampaignEvent')),('mobile_message_models',('MobileMessageRecord','MobileMessageEvent')),('inbox_models',('InboxRecord','InboxEvent')),('ads_models',('AdsRecord','AdsEvent'))]:
  models=importlib.import_module(path+'.'+module)
  with connection.schema_editor() as e:
   for name in classes:
    model=getattr(models,name)
    if model._meta.db_table not in connection.introspection.table_names():e.create_model(model)
from apps.prestadores.mi_negocio.gestion_comercial.sales.models import Opportunity,StageHistory
with connection.schema_editor() as e:
 for model in (Opportunity,StageHistory):
  if model._meta.db_table not in connection.introspection.table_names():e.create_model(model)
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:
 base=f['cases'](system,path)
 class Checks(RecoveryCases,OperationsCases,base):pass
 suite.addTests(Checks(n) for n in unittest.defaultTestLoader.getTestCaseNames(RecoveryCases))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
