"""Exact Python application default; no database default or historical rewrite."""
from decimal import Decimal
from django.db import migrations,models

class Migration(migrations.Migration):
    dependencies=[('core_erp','0006_accounting_guard_schema')]
    operations=[migrations.SeparateDatabaseAndState(
        database_operations=[],
        state_operations=[migrations.AlterField(model_name='journalentry',name='exchange_rate',field=models.DecimalField(max_digits=18,decimal_places=6,default=Decimal('1.000000')))],
    )]
