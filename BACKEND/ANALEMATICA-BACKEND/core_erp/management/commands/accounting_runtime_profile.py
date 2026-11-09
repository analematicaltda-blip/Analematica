"""Print a reviewable accounting permission specification; never applies grants."""
import json
from django.core.management.base import BaseCommand
from apps.core_erp.accounting.runtime_profile import describe_profile

class Command(BaseCommand):
    help='Describe core accounting DML/row-lock privileges. Does not grant access.'
    def handle(self,*args,**options):self.stdout.write(json.dumps(describe_profile(),sort_keys=True))
