"""Explicit operator conversion of legacy TOTP secrets; never prints secret values."""
import base64
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from allauth.mfa.models import Authenticator
from apps.common.mfa_adapter import EncryptedMFAAdapter,PREFIX

class Command(BaseCommand):
    help='Audit legacy TOTP storage; --apply encrypts reviewed records in place.'
    def add_arguments(self,parser):parser.add_argument('--apply',action='store_true')
    @transaction.atomic
    def handle(self,*args,**options):
        adapter=EncryptedMFAAdapter();count=0
        query=Authenticator.objects.filter(type='totp').order_by('pk')
        if options['apply']:query=query.select_for_update()
        for factor in query:
            text=factor.data.get('secret')
            if not isinstance(text,str):raise CommandError('Registro MFA inválido; no se aplicó la conversión.')
            if text.startswith(PREFIX):
                try:adapter.decrypt(text)
                except Exception:raise CommandError('No se pudo verificar el cifrado existente; no se aplicó la conversión.')
                continue
            try:
                if len(text)>512 or len(base64.b32decode(text,casefold=True))<16:raise ValueError()
            except Exception:raise CommandError('Registro TOTP inválido; no se aplicó la conversión.')
            count+=1
            if options['apply']:
                factor.data={**factor.data,'secret':adapter.encrypt(text)};factor.save(update_fields=['data'])
        self.stdout.write(('ENCRYPTED ' if options['apply'] else 'REQUIRES_REVIEW_NO_WRITE ')+str(count))
