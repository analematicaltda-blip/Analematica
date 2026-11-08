"""Trusted operator entry point. Evidence is a digest, never document contents."""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand,CommandError
from django.utils import timezone
from apps.turismo.services.company_identity import review_link

class Command(BaseCommand):
    help='Validate a tourism/accounting identity link; dry-run by default.'
    def add_arguments(self,parser):
        parser.add_argument('--operator',required=True,type=int)
        parser.add_argument('--provider',required=True)
        parser.add_argument('--tenant',required=True)
        parser.add_argument('--evidence-sha256',required=True)
        parser.add_argument('--days',type=int,default=7)
        parser.add_argument('--apply',action='store_true')
    def handle(self,*args,**options):
        try:
            operator=get_user_model().objects.get(pk=options['operator'])
            link=review_link(operator=operator,provider_id=options['provider'],tenant_id=options['tenant'],evidence_digest=options['evidence_sha256'],valid_until=timezone.now()+timedelta(days=options['days']),apply=options['apply'])
        except Exception as exc:
            raise CommandError('Revisión rechazada; comprobar autoridad, identidad, vigencia y vínculos previos.') from exc
        self.stdout.write('APPLIED' if options['apply'] else 'VALIDATED_ONLY_NO_WRITE')
