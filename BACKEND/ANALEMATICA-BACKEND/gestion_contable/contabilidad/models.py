from apps.core_erp.accounting.models import (
    Account as CoreAccount,
    JournalEntry as CoreJournalEntry,
    LedgerEntry as CoreJournalLine,
    FiscalPeriod as CoreFiscalPeriod,
    ChartOfAccounts as CoreChartOfAccounts
)
from django.db import models

class AdminChartOfAccounts(CoreChartOfAccounts):
    class Meta:
        proxy = True
        app_label = 'admin_contabilidad'
        verbose_name = "Admin Chart of Accounts"

class AdminAccount(CoreAccount):
    class Meta:
        proxy = True
        app_label = 'admin_contabilidad'

class AdminFiscalPeriod(CoreFiscalPeriod):
    class Meta:
        proxy = True
        app_label = 'admin_contabilidad'

class AdminJournalEntry(CoreJournalEntry):
    class Meta:
        proxy = True
        app_label = 'admin_contabilidad'

class AdminAccountingTransaction(CoreJournalLine):
    class Meta:
        proxy = True
        app_label = 'admin_contabilidad'
