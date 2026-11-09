"""Inspect privileges without granting, revoking, printing identities or credentials."""
import json
from django.core.management.base import BaseCommand,CommandError
from django.db import connection,DatabaseError
from apps.core_erp.accounting.db_privileges import inspect_privileges

class Command(BaseCommand):
    help='Read-only PostgreSQL privilege-boundary check for guarded accounting tables.'
    def add_arguments(self,parser):parser.add_argument('--require-ready',action='store_true')
    def handle(self,*args,**options):
        try:report=inspect_privileges(connection)
        except DatabaseError:raise CommandError('Privilege audit unavailable; check database access. No SQL errors or credentials are printed.') from None
        self.stdout.write(json.dumps(report,sort_keys=True))
        if options['require_ready'] and not report['ready']:raise CommandError('Accounting database privilege boundary is not ready.')
