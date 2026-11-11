"""Protect existing worker evidence without rewriting any row or original migration."""
from django.db import migrations
TABLES=('sg_sst_professionalauthorization','sg_sst_ppeassignment','sg_sst_workperiod','sg_sst_workperiodend','sg_sst_restperiod','sg_sst_safetyrevocation')
def forward(apps,schema_editor):
 connection=schema_editor.connection
 if connection.vendor!='postgresql':return
 q=connection.ops.quote_name
 with connection.cursor() as c:
  for table in TABLES:c.execute(f'CREATE TRIGGER {q("safety_truncate_"+table)} BEFORE TRUNCATE ON {q(table)} FOR EACH STATEMENT EXECUTE FUNCTION {q("safety_guard_"+table)}()')
def backward(apps,schema_editor):
 connection=schema_editor.connection
 if connection.vendor!='postgresql':return
 q=connection.ops.quote_name
 with connection.cursor() as c:
  for table in TABLES:c.execute(f'DROP TRIGGER {q("safety_truncate_"+table)} ON {q(table)}')
class Migration(migrations.Migration):
 dependencies=[('sg_sst','0001_initial')]
 operations=[migrations.RunPython(forward,backward)]
