import logging
from decimal import Decimal
from django.db.models import Sum
from apps.core_erp.accounting.models import JournalEntry, LedgerEntry, Account
from apps.core_erp.tenancy.models import Tenant

logger = logging.getLogger(__name__)

class FinancialIntegrityMonitor:
    """
    Financial system immune system.
    Detects anomalies and structural violations in the ledger.
    """

    @staticmethod
    def run_daily_check():
        """
        Runs all integrity checks for all tenants.
        """
        results = {}
        tenants = Tenant.objects.all()

        for tenant in tenants:
            tenant_results = {
                'unbalanced_entries': FinancialIntegrityMonitor.check_unbalanced_entries(tenant.id),
                'negative_assets': FinancialIntegrityMonitor.check_negative_assets(tenant.id),
                'double_posted_events': FinancialIntegrityMonitor.check_double_posting(tenant.id)
            }
            results[str(tenant.id)] = tenant_results

        return results

    @staticmethod
    def check_unbalanced_entries(tenant_id):
        """
        Verifies that all posted journal entries are balanced (Debit = Credit).
        """
        unbalanced = []
        entries = JournalEntry.objects.filter(tenant_id=tenant_id, is_posted=True)

        for entry in entries:
            totals = entry.lines.aggregate(
                d=Sum('debit_amount'),
                c=Sum('credit_amount')
            )
            d = totals['d'] or Decimal('0.00')
            c = totals['c'] or Decimal('0.00')

            if abs(d - c) > Decimal('0.001'):
                unbalanced.append({
                    'entry_id': str(entry.id),
                    'debit': float(d),
                    'credit': float(c),
                    'diff': float(d - c)
                })

        if unbalanced:
            logger.error(f"INTEGRITY ALERT: {len(unbalanced)} unbalanced entries found for tenant {tenant_id}")
        return unbalanced

    @staticmethod
    def check_negative_assets(tenant_id):
        """
        Detects asset accounts with credit balances (often an error).
        """
        anomalies = []
        # Cuentas de Activo (1)
        asset_accounts = Account.plain_objects.filter(tenant_id=tenant_id, code__startswith='1')

        for account in asset_accounts:
            totals = LedgerEntry.objects.filter(
                journal_entry__tenant_id=tenant_id,
                journal_entry__is_posted=True,
                account=account
            ).aggregate(
                d=Sum('debit_amount'),
                c=Sum('credit_amount')
            )
            d = totals['d'] or Decimal('0.00')
            c = totals['c'] or Decimal('0.00')

            balance = d - c
            if balance < 0:
                anomalies.append({
                    'account_code': account.code,
                    'balance': float(balance)
                })
        return anomalies

    @staticmethod
    def check_double_posting(tenant_id):
        """
        Detects if an event (by idempotency or reference) was posted twice.
        """
        # Checks for duplicate references in the same day for same tenant
        duplicates = []
        # Simplificando: buscar referencias duplicadas en JournalEntry
        from django.db.models import Count
        dupes = JournalEntry.objects.filter(tenant_id=tenant_id).values('reference').annotate(c=Count('id')).filter(c__gt=1)

        for d in dupes:
            if d['reference']:
                duplicates.append(d['reference'])

        return duplicates
