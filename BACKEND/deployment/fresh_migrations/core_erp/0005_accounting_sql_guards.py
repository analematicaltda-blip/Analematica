"""Protect already posted records and reviewed policy history in the database."""
from django.db import migrations

def forwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_guards import install
    install(schema_editor.connection)

def backwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_guards import uninstall
    uninstall(schema_editor.connection)

class Migration(migrations.Migration):
    dependencies=[('core_erp','0004_accounting_ratio_policy')]
    operations=[migrations.RunPython(forwards,backwards)]
