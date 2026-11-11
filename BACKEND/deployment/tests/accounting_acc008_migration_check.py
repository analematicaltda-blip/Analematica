"""Replay the additive CRM migration on legacy rows in an isolated fixture."""
import runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal
f=runpy.run_path(str(Path(__file__).with_name('accounting_invoice_queue_check.py')),run_name='crm_migration_fixture')
from django.db import connection
from django.db.migrations.state import ProjectState
ROOT=Path(__file__).resolve().parents[3]
class CRMContractMigration(unittest.TestCase):
 def test_legacy_values_preserved_without_inventing_plan_or_probability(self):
  assert connection.vendor=='sqlite'
  paths=[ROOT/'BACKEND/SGA-TUR-BAKEND/apps/comercial/migrations',ROOT/'BACKEND/deployment/fresh_migrations/comercial']
  state=ProjectState()
  for operation in runpy.run_path(str(paths[0]/'0001_initial.py'))['Migration'].operations:operation.state_forwards('comercial',state)
  Lead=state.apps.get_model('comercial','Lead');Opportunity=state.apps.get_model('comercial','Opportunity')
  self.assertNotIn(Lead._meta.db_table,connection.introspection.table_names());self.assertNotIn(Opportunity._meta.db_table,connection.introspection.table_names())
  with connection.schema_editor() as editor:editor.create_model(Lead);editor.create_model(Opportunity)
  lead=Lead.objects.create(name='Legacy synthetic',email=uuid.uuid4().hex+'@example.test');old=Opportunity.objects.create(lead=lead,stage='won',estimated_revenue=Decimal('123.45'))
  before=(old.pk,old.lead_id,old.stage,old.estimated_revenue)
  migration=runpy.run_path(str(paths[0]/'0002_crm_opportunity_contract.py'))['Migration']
  for operation in migration.operations:
   after=state.clone();operation.state_forwards('comercial',after)
   with connection.schema_editor() as editor:operation.database_forwards('comercial',editor,state,after)
   state=after
  New=state.apps.get_model('comercial','Opportunity');actual=New.objects.get(pk=old.pk);actual_lead=state.apps.get_model('comercial','Lead').objects.get(pk=lead.pk)
  self.assertEqual(before,(actual.pk,actual.lead_id,actual.stage,actual.estimated_revenue));self.assertIsNone(actual.probability);self.assertEqual(actual.expected_plan,'');self.assertEqual(actual_lead.industry,'');self.assertEqual(actual_lead.company_size,'')
  # The alternate fresh schema has exactly the same operations/field metadata.
  mirror=runpy.run_path(str(paths[1]/'0002_crm_opportunity_contract.py'))['Migration']
  self.assertEqual([str(op.describe()) for op in migration.operations],[str(op.describe()) for op in mirror.operations])
  from apps.comercial.models import Lead as CurrentLead,Opportunity as CurrentOpportunity
  for model,current,fields in [(actual_lead.__class__,CurrentLead,['industry','company_size']),(New,CurrentOpportunity,['expected_plan','probability','stage'])]:
   for field in fields:self.assertEqual(model._meta.get_field(field).deconstruct()[1:],current._meta.get_field(field).deconstruct()[1:])
if __name__=='__main__':unittest.main()
