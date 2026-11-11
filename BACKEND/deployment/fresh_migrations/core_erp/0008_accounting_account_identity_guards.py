"""Add account identity protection without changing historical amounts/hashes."""
from django.db import migrations

def forwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_identity_guards import install
    install(schema_editor.connection)

def backwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_identity_guards import uninstall
    uninstall(schema_editor.connection)

class Migration(migrations.Migration):
    dependencies=[('core_erp','0007_accounting_exact_rate_default')]
    operations=[migrations.RunPython(forwards,backwards)]
