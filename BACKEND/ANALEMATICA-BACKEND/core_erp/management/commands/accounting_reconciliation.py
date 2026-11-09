"""Read-only bounded reconciliation inventory; never repairs financial history."""
import json
from uuid import UUID
from django.core.management.base import BaseCommand,CommandError
from django.db import DatabaseError
from apps.core_erp.accounting.reconciliation import inspect_company
from apps.core_erp.accounting.exceptions import AccountingError

class Command(BaseCommand):
    help='Inspect company ledger reconciliation findings. No writes or rehashing.'
    def add_arguments(self,parser):
        parser.add_argument('--tenant',type=UUID,required=True)
        parser.add_argument('--after-id',type=UUID)
        parser.add_argument('--limit',type=int,default=20)
    def handle(self,*args,**options):
        try:report=inspect_company(options['tenant'],after_id=options['after_id'],limit=options['limit'])
        except (AccountingError,DatabaseError):raise CommandError('Reconciliation diagnostic unavailable; check scope, limits and schema. No SQL errors are printed.') from None
        self.stdout.write(json.dumps(report,sort_keys=True))
