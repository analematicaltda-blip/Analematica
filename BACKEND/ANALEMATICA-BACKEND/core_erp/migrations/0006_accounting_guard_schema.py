"""Prevent temporary-table shadowing in the PostgreSQL parent lookup."""
from django.db import migrations

def forwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_guard_hardening import install
    install(schema_editor.connection)

def backwards(apps,schema_editor):
    from apps.core_erp.accounting.sql_guards import install
    install(schema_editor.connection)

class Migration(migrations.Migration):
    dependencies=[('core_erp','0005_accounting_sql_guards')]
    operations=[migrations.RunPython(forwards,backwards)]
