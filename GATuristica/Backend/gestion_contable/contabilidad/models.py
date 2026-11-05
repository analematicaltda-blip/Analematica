from apps.core_erp.accounting.models import (
    Account as CoreAccount,
    JournalEntry as CoreJournalEntry,
    LedgerEntry as CoreJournalLine,
    FiscalPeriod as CoreFiscalPeriod,
    ChartOfAccounts as CoreChartOfAccounts
)
from django.db import models

class PlanDeCuentas(CoreChartOfAccounts):
    class Meta:
        proxy = True
        app_label = 'contabilidad'

class Cuenta(CoreAccount):
    class Meta:
        proxy = True
        app_label = 'contabilidad'

class PeriodoContable(CoreFiscalPeriod):
    class Meta:
        proxy = True
        app_label = 'contabilidad'

class AsientoContable(CoreJournalEntry):
    class Meta:
        proxy = True
        app_label = 'contabilidad'

class Transaccion(CoreJournalLine):
    class Meta:
        proxy = True
        app_label = 'contabilidad'
