"""Read-only by default; explicitly apply the local accounting projector per company."""
import json
from uuid import UUID
from django.core.management.base import BaseCommand,CommandError
from django.db import DatabaseError
from apps.core_erp.accounting import delivery
from apps.core_erp.accounting.exceptions import AccountingError

class Command(BaseCommand):
    help='Inspect or apply the local accounting projection. No external publishing or payments.'
    def add_arguments(self,parser):
        parser.add_argument('--tenant',type=UUID,required=True)
        parser.add_argument('--limit',type=int,default=50)
        parser.add_argument('--apply',action='store_true')
    def handle(self,*args,**options):
        try:
            delivery.bounded_limit(options['limit'])
            result={'mode':'APPLY' if options['apply'] else 'READ_ONLY','local_only':True}
            if options['apply']:result['batch']=delivery.run_batch(options['tenant'],options['limit'])
            result['projection']=delivery.status(options['tenant'])
            result['projection'].pop('balances',None)
            result['financial_values_omitted']=True
        except (AccountingError,DatabaseError):
            raise CommandError('Projection unavailable: check feature flag, company, schema and integrity. No secrets are printed.') from None
        self.stdout.write(json.dumps(result,sort_keys=True,default=str))
