"""Erase unusable pending TOTP material, retaining audit metadata and active factors."""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from apps.turismo.models import ErpTotpEnrollment


class Command(BaseCommand):
    help = 'Preview expired/consumed enrollment cleanup; --apply erases pending ciphertext only.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--batch-size', type=int, default=500)

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        if not 1 <= batch_size <= 10000:
            raise CommandError('batch-size debe estar entre 1 y 10000.')
        # Fixed cutoff: no still-valid proposal becomes eligible during this batch.
        cutoff = timezone.now()
        eligible = ErpTotpEnrollment.objects.filter(
            Q(expires_at__lte=cutoff) | Q(consumed_at__isnull=False)
        ).exclude(sealed_secret='')
        identifiers = list(eligible.order_by('created_at', 'pk').values_list('pk', flat=True)[:batch_size])
        count = len(identifiers)
        if options['apply']:
            # Recheck eligibility in the UPDATE itself: safe against concurrent requests.
            # Do not touch Authenticator, usage counters, sessions or retained metadata.
            count = eligible.filter(pk__in=identifiers).update(sealed_secret='')
        self.stdout.write(('ERASED ' if options['apply'] else 'ELIGIBLE_NO_WRITE ') + str(count))
